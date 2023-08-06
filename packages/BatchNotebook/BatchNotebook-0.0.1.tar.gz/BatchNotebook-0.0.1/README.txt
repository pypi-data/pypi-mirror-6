=============
BatchNotebook
=============

Why Use This Library
--------------------

1. Explore data by writing an series of IPython notebooks.
2. The Data are updated. Rerun all notebooks.
3. Use nbconvert to generate reports from the executed notebooks.

This library saves time on step 2. That is, it allows you to rerun your
notebooks from the command line, in batch mode, rather than running them
manually or hacking together some browser runner with Selenium or something
similar. It assumes that your executed notebook(s) will be used as a reporting
tool (e.g. you want the inline html graphs.) If you do not need to use the
executed notebook as a report, this library is not necessary; there are other
scripts that can extract the code and turn it into a plain old py script.

According to `this stackoverflow post <http://stackoverflow.com/questions/17905350/running-an-ipython-notebook-non-interactively>`_,
non-interactive IPython notebook execution will be added to the 2.0 core. Until
then, I patched together this library from the work of others.

How To Use This Library
-----------------------

This library installs a script ``run_ipython_script.py``. The following is the
output of of ``run_ipython_script.py --help``::

    usage: run_ipython_script.py [-h] [--timeout TIMEOUT] [--verbose] src dst

    Run IPython notebook scripts in batch mode.

    positional arguments:
      src                   source notebook path
      dst                   destination notebook path

    optional arguments:
      -h, --help            show this help message and exit
      --timeout TIMEOUT, -T TIMEOUT
                            max execution time in seconds per cell
      --verbose, -V         print status messages as processing proceeds


Caveats
-------

Don't use ``print``. I'm not an IPython developer so I can't explain why
something does or does not work, but calls to print will break the output.
Instead, do ``from IPython.display import HTML`` and return the HTML object
in a cell where you want printed string output.

Contributing
------------

If you have any bug fixes or contributions, please send a pull request to the
`BatchNotebook repository on github <https://github.com/jbn/BatchNotebook>`_.
However, please keep in mind *this library is a temporary workaround to a
problem that is being addressed by those developers who know IPython best*.
Therefore, you may want lend your typing hands to the next IPython 2.0 core,
rather than me.

See also
--------

This library was based off of:
`this <https://gist.github.com/minrk/2620735>`_ and
`this <https://gist.github.com/davidshinn/6110231/raw/bb7efbac56e8c007eb24f5dc057896b7a07db1bb/ipnbdoctest.py>`_.

Acknowledgements
----------------
This library was written to generate reports for a project funded by AFRL,
managed by JHU/APL. I (John B Nelson) am the sole author, and I am responsible
for any bugs or errors.
