# coding=utf-8
"""
Argument module
"""
__author__ = 'Alisue <lambdalisue@hashnote.net>'
import os
import argparse
import itertools
import matplotlib as mpl


def get_supported_filetypes():
    """
    Get matplotlib supported filetypes
    """
    fig = mpl.figure.Figure()
    fcb = mpl.backends.backend_agg.FigureCanvasBase(fig)
    return list(fcb.get_supported_filetypes().keys())


def parse_colors(colors):
    """
    Parse comma separated HTML colors

    Examples
    --------
    >>> parse_colors("#000000")
    ['#000000']
    >>> parse_colors('#000000,#111111')
    ['#000000', '#111111']
    >>> parse_colors('#000000,#111111, #222222')
    ['#000000', '#111111', '#222222']
    >>> parse_colors(None) == mpl.rcParams['axes.color_cycle']
    True
    """
    if colors:
        colors = colors.split(",")
        colors = [x.strip() for x in colors]
    else:
        colors = mpl.rcParams['axes.color_cycle']
    return colors


def parse_args(args):
    supported_filetypes = get_supported_filetypes()

    parser = argparse.ArgumentParser()
    # matplotlib intialization
    parser.add_argument('-r', '--rc-file', default=None,
                        help=("A filename of matplotlib RC file will be loaded. "
                              "You can specify the absolute path or relative "
                              "path. If you specify it with relative path, the "
                              "relative path from working directory will be "
                              "used."))
    parser.add_argument('--colors', default=None,
                        help=("A comma separated HTML colors."))
    # load options
    parser.add_argument('infiles', nargs="*")
    parser.add_argument('--parser', default=None,
                        help=("A maidenhair parser name."))
    parser.add_argument('--loader', default=None,
                        help=("A maidenhair loader name."))
    parser.add_argument('--recursive', default=False, action='store_true',
                        help=("Recursively load data from a directory."))
    parser.add_argument('--reverse', default=False, action='store_true',
                        help=("Reverse data loading order."))
    parser.add_argument('--relative', default=False, action='store_true',
                        help=("Translate data to relative value to the 1st "
                              "data loaded."))
    # save options
    parser.add_argument('-o', '--output',
                        help=("An output graph file. File type will be "
                              "automatically detected from the extensions. "
                              "Or you can specify the file type with "
                              "--format option."))
    parser.add_argument('-f', '--format', default=None,
                        choices=supported_filetypes,
                        help=("An output graph file type."))
    # plot options
    parser.add_argument('-m', '--mode', default='curve',
                        choices=['curve', 'transition'],
                        help=("A mode of plotting. "
                              "'curve' is used for plotting relation between X "
                              "and Y data. 'transition' is used for plotting "
                              "relation among X1-Xn and Y1-Yn data."))
    parser.add_argument('-t', '--theme', default='light',
                        choices=['light', 'dark'],
                        help=("A theme of plotting. "))
    # graph options
    parser.add_argument('--width', default=10, type=float,
                        help=("A width in inch of output graph."))
    parser.add_argument('--height', default=8, type=float,
                        help=("A height in inch of output graph."))
    parser.add_argument('--xlabel', default=None,
                        help=("A label text of X axis."))
    parser.add_argument('--ylabel', default=None,
                        help=("A label text of Y axis."))
    parser.add_argument('--ylabel2', default=None,
                        help=("A label text of Y2 axis used in "
                              "'transition' mode."))
    parser.add_argument('--xmin', type=float, default=None,
                        help=("Limit minimum value of X axis."))
    parser.add_argument('--xmax', type=float, default=None,
                        help=("Limit maximum value of X axis."))
    parser.add_argument('--ymin', type=float, default=None,
                        help=("Limit minimum value of Y axis."))
    parser.add_argument('--ymax', type=float, default=None,
                        help=("Limit maximum value of Y axis."))
    parser.add_argument('--ymin2', type=float, default=None,
                        help=("Limit minimum value of Y2 axis used in "
                              "'transition' mode."))
    parser.add_argument('--ymax2', type=float, default=None,
                        help=("Limit maximum value of Y2 axis used in "
                              "'transition' mode."))
    parser.add_argument('--without-legend', dest='legend', default=True,
                        action='store_false',
                        help=("Disable legend drawing."))
    # parse command arguments
    args = parser.parse_args(args)
    # extra parse
    BASE_DIR = os.path.dirname(__file__)
    mpl.rc_file(os.path.join(BASE_DIR, 'rc', args.theme + ".rc"))
    args.colors = parse_colors(args.colors)
    args.colors = itertools.cycle(args.colors)
    return args

if __name__ == '__main__':
    import doctest; doctest.testmod()
