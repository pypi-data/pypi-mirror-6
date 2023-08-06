#!python

import argparse
import batch_notebook

if __name__ == '__main__':
    desc = 'Run IPython notebook scripts in batch mode.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('src', help='source notebook path')
    parser.add_argument('dst', help='destination notebook path')
    parser.add_argument('--timeout', '-T',
                        help='max execution time in seconds per cell',
                        type=int)
    parser.add_argument('--verbose', '-V', action='store_true',
                        help='print status messages as processing proceeds')

    args = parser.parse_args()

    kwargs = {}
    if args.timeout:
        kwargs['timeout'] = args.timeout
    if args.verbose:
        kwargs['verbose'] = args.verbose

    batch_notebook.run_and_save(args.src, args.dst, **kwargs)
