"""
Module for running all the cells in an IPython notebook in batch mode, then
saving the result -- with output cells -- to a separate notebook.

Usage pattern
-------------

1. Explore data by writing an series of IPython notebooks.
2. The data are updated. Rerun all notebooks.
3. Use nbconvert to generate reports from the executed notebooks.

Implementation
--------------
I am not an IPython developer. I know almost nothing about its internals. This
library was hacked together by making inferences from other people's work.

In particular, see:

1. https://gist.github.com/minrk/2620735
2. https://gist.github.com/davidshinn/6110231/raw/bb7efbac56e8c007eb24f5dc057896b7a07db1bb/ipnbdoctest.py
"""
from __future__ import print_function

import io

try:
    from Queue import Empty  # Python 2.X
except ImportError:
    from queue import Empty  # Python 3.X

try:
    from IPython.kernel import KernelManager
except ImportError:
    from IPython.zmq.blockingkernelmanager import BlockingKernelManager as KernelManager

from IPython.nbformat.current import reads, NotebookNode, write

def run_cell(km, cell, timeout=20):
    shell = km.shell_channel
    iopub = km.iopub_channel
    shell.execute(cell.input)
    shell.get_msg(timeout=timeout)

    outs = []
    while True:
        try:
            msg = iopub.get_msg(timeout=0.2)
        except Empty:
            break

        msg_type = msg['msg_type']
        if msg_type in ('status', 'pyin'):
            continue
        elif msg_type == 'clear_output':
            outs = []
            continue

        content = msg['content']
        out = NotebookNode(output_type=msg_type)

        if msg_type == 'stream':
            out.stream = content['name']
            out.txt = content['data']
        elif msg_type in ('display_data', 'pyout'):
            for mime, data in content['data'].items():
                attr = mime.split('/')[-1].lower()
                attr = attr.replace('+xml', '').replace('plain', 'text')
                setattr(out, attr, data)
            if msg_type == 'pyout':
                out.prompt_number = content['execution_count']
        elif msg_type == 'pyerr':
            out.ename = content['ename']
            out.evalue = content['evalue']
            out.traceback = content['traceback']
        else:
            print("unhandled iopub msg:", msg_type)

        outs.append(out)
        cell.outputs = outs

    return outs


def run_notebook(nb, pylab_inline=True, timeout=20):
    """
    Run the notebook, populating the output cells with appropriate content.

    Params
    ------
    nb : the contents of a notebook as a string
    pylab_inline : i.e. should the command be executed as if it was flagged with
                   --paylab=inline
    timeout : the length of time in seconds to wait before the script is
              considered timed out. I set this to a big value for some
              data heavy scripts
    """
    # Start the kernel.
    km = KernelManager()
    args = {}
    if pylab_inline:
        args['extra_arguments'] = ['--pylab=inline']
    km.start_kernel(**args)

    # Get our client.
    try:
        kc = km.client()
    except AttributeError:
        kc = km
    kc.start_channels()
    shell = kc.shell_channel

    # Ping the kernel.
    shell.execute('pass')
    shell.get_msg()

    # Run all the cells.
    cells_executed, cells_failed = 0, 0
    for ws in nb.worksheets:
        for cell in ws.cells:
            cell.prompt_number = cells_executed + 1
            if cell.cell_type != 'code':
                continue

            cells_executed += 1
            run_cell(kc, cell, timeout)

    # Clean up resources. (Hopefully?)
    kc.stop_channels()
    km.shutdown_kernel()
    del km

    return cells_failed


def run_and_save(src_notebook, dst_notebook, verbose=False, **kwargs):
    """
    Run a notebook; populate its output cells; save as a new notebook.

    Params
    ------
    src_notebook : file path of the source notebook
    dst_notebook : file path of the location to save the executed notebook
    verbose : set to true if for printed status messages
    kwargs : passed to `run_notebook`
    """
    if verbose:
        print("Running %s" % src_notebook)

    with open(src_notebook) as f:
        nb = reads(f.read(), 'json')

    n_errors = run_notebook(nb, **kwargs)
    if verbose:
        print("\tNumber of errors: %d" % n_errors)

    if verbose:
        print("\tSaving to destination %s" % dst_notebook)

    with io.open(dst_notebook, 'w', encoding='utf8') as f:
        write(nb, f, 'json')

    if verbose:
        print("\tDone!")

    return n_errors
