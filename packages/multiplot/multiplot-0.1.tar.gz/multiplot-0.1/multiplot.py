#! /usr/bin/env python
"""
multiplot - squeeze multiple images into one page.

Usage:
    multiplot.py [-k] [-p <per-page>] [-o <output>] <input> ...
    multiplot.py (-h | --help | -v | --version)

Options:
    -k --keep       Keep temporary files
    -p <count>      Set number of images per page
    -o <output>     Set output file name (default is 'multi.pdf')
    -h --help       Show this help
    -v --version    Show version number

"""
from __future__ import division
import os
import subprocess
from math import sqrt

__all__ = ['main']

def page(files):
    """Assemble TeX code for page including the given graphics."""
    # compute layout
    log2 = (len(files)-1).bit_length()
    rows = 2 ** ((log2 + 1) // 2)
    cols = 2 ** (log2 // 2)
    width = r'{%s\textwidth}' % ((1 / cols) - 0.02,)
    height = r'{%s\textheight}' % ((1 / rows) - 0.02,)
    # head
    yield r'''
\begin{figure}
  \centering
  \begin{tabular}{%s}
''' % ('c' * cols,)
    # graphics
    for r in range(rows):
        for c in range(cols):
            i = r*cols + c
            nl = r'\\' if c+1 == cols else '&'
            if i < len(files):
                base, ext = os.path.splitext(os.path.abspath(files[i]))
                file = '{%s}%s' % (base, ext)
                yield r'\includegraphics[width=%s,height=%s,keepaspectratio]{%s}%s' % (width, height, file, nl)
            else:
                yield nl
    # foot
    yield r'''
  \end{tabular}
\end{figure}
'''

def document(files, per_page=None):
    """
    """
    if not files:
        raise ValueError("Must specify at least one image!")
    if not per_page:
        per_page = len(files)
    # head
    if (per_page-1).bit_length() % 2:
        yield r'\documentclass{article}'
    else:
        yield r'\documentclass[landscape]{article}'
    yield r'''
\usepackage{graphicx}
\usepackage{geometry}'''
    xs, ys = sqrt(2), 1
    margin = 'left={0}cm,right={0}cm,top={1}cm,bottom={1}cm'.format(xs, ys)
    yield r'\geometry{a4paper,%s}' % (margin,)
    yield r'\begin{document}'
    yield r'\pagestyle{empty}'
    # pages
    for p in range((len(files)+per_page-1) // per_page):
        for line in page(files[p*per_page:(p+1)*per_page]):
            yield line
    # foot
    yield r'\end{document}'


def pdflatex(text, output, keep=False):
    """
    Call pdflatex on the given TeX lines.
    """
    base, ext = os.path.splitext(os.path.abspath(output))
    path, name = os.path.split(base)
    with open(base+'.tex', 'wt') as f:
        f.write('\n'.join(text))
    subprocess.call([
        'pdflatex',
        '-interaction=batchmode',
        '--output-directory='+path,
        base+'.tex'
    ])
    if not keep:
        os.remove(base+'.aux')
        os.remove(base+'.log')
        os.remove(base+'.tex')

def mkint(arg):
    return int(arg) if arg else arg

def main():
    from docopt import docopt
    arguments = docopt(__doc__, version='multiplot 0.1')
    pdflatex(document(arguments['<input>'],
                      per_page=mkint(arguments['-p'])),
             output=arguments['-o'] or 'multi.pdf',
             keep=arguments['--keep'])
    return 0
main.__doc__ = __doc__

if __name__ == '__main__':
    main()
