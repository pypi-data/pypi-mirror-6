"""Main driver implementation."""

from docopt import docopt
from os.path import basename

from . import plugin

def generate_plugin(src, dst, plugin_name):
    with open(dst, 'wb') as f:
        with plugin.Plugin(f, plugin_name, plugin.from_fs(src)) as plg:
            plg.import_from_manifest()

def cronoplug(args, generate = generate_plugin):
    """Usage: cronoplug [options] <src> <dst>

    -n, --name <name>   Plugin name"""
    arguments = docopt(cronoplug.__doc__, args)
    srcdir = arguments['<src>']
    dstfile = arguments['<dst>']
    plgname = arguments['--name']
    if plgname is None:
        plgname = basename(srcdir)
    generate(srcdir, dstfile, plgname)

if __name__ == '__main__':
    from sys import argv
    cronoplug(argv[1:])

