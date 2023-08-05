#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
from optparse import OptionParser
from .conv import Converter
from . import templates
VERSION = "0.2.0"


def run():
    parser = OptionParser(usage="usage: %prog [options] file1 file2 ...")
    parser.version = VERSION
    parser.add_option('-f', '--file',
                      dest="filename",
                      metavar="FILE",
                      help=("File to which to save. It will be loaded if "
                            "file exists and contains result of image2py"),
                      default=None)
    parser.add_option("-t", "--template",
                      action="store",
                      dest="template",
                      default=None,
                      help="template of output (qt, pyqt, pyside)")
    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.print_help()
        sys.exit(0)
    try:
        conv = Converter(options.filename)
        if options.template is not None:
            conv.set_template(templates.templateByName(options.template))
        for item in args:
            conv.add_file(item)
        if options.filename is None:
            print(conv.output())
        else:
            conv.save(options.filename)
            print("File has been saved")
    except Exception as e:
        print('Error: {!s}'.format(e))


if __name__ == "__main__":
    run()
