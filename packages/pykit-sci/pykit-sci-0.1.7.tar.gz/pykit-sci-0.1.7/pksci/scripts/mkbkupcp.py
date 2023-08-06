# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
=======================================================================
script for batch filename ext change (:mod:`pksci.scripts.mkbkupcp`)
=======================================================================

.. currentmodule:: pksci.scripts.mkbkupcp

.. todo::

   Add option to copy backup file to secondary dst.

.. todo::

   handle exceptions

.. argparse::
   :module: pksci.scripts.mkbkupcp
   :func: _argparser
   :prog: mkbkupcp

"""
from __future__ import absolute_import, print_function, division

import argparse
import os
import shutil
import sys
from datetime import datetime


def printmsg(src, dst, srctype):
    print('copied source {!s}: {!s}\n'.format(srctype, src) +
          'to backup {!s}: {!s}'.format(srctype, dst))


def _argparser():
    parser = argparse.ArgumentParser()
    default_backup_ext = '.backup_' + \
        datetime.now().strftime("%Y-%m-%d_%H%M%S")
    parser.add_argument('--backup_ext', default=default_backup_ext,
                        help='backup extension (default: %(default)s)')
    parser.add_argument('src_files', nargs='+',
                        help='files to backup')
    return parser


def main():

    args = _argparser().parse_args()
    backup_ext = args.backup_ext
    files = args.src_files
    if sys.platform == 'win32':
        from glob import glob
        files = glob(files[0])
    for src in files:
        bkupstr = backup_ext
        dst = src + bkupstr
        if os.path.isfile(src):
            shutil.copy2(src, dst)
            printmsg(src, dst, 'file')
        elif os.path.isdir(src):
            shutil.copytree(src, dst)
            printmsg(src, dst, 'directory')

if __name__ == '__main__':
    sys.exit(main())
