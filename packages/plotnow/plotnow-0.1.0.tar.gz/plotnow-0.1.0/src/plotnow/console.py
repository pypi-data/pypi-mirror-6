#!/usr/bin/env python
# coding=utf-8
"""
"""
__author__ = 'Alisue <lambdalisue@hashnote.net>'
import os
import matplotlib as mpl
import matplotlib.pyplot as pl
import maidenhair
import plotnow.plots
import plotnow.loader
import plotnow.arguments

def limit_xaxis(ax, xmin=None, xmax=None):
    _xmin, _xmax = ax.get_xlim()
    if xmin is not None:
        _xmin = xmin
    if xmax is not None:
        _xmax = xmax
    ax.set_xlim(_xmin, _xmax)

def limit_yaxis(ax, ymin=None, ymax=None):
    _ymin, _ymax = ax.get_ylim()
    if ymin is not None:
        _ymin = ymin
    if ymax is not None:
        _ymax = ymax
    ax.set_ylim(_ymin, _ymax)

def main(args=None):
    # parse specified command arguments
    args = plotnow.arguments.parse_args(args)
    # initialize matplotlib
    if args.rc_file:
        mpl.rc_file(args.rc_file)
    # initialize maidenhair
    if args.parser:
        maidenhair.set_default_parser(args.parser)
    if args.loader:
        maidenhair.set_default_loader(args.loader)

    # create figure and initialize
    pl.figure(figsize=(args.width, args.height))
    ax1 = pl.gca()
    if args.mode == 'transition':
        ax2 = ax1.twinx()

    # plot
    for infile in args.infiles:
        basename = os.path.basename(infile)
        dataset = plotnow.loader.load(infile,
                                      recursive=args.recursive,
                                      reverse=args.reverse,
                                      relative=args.relative)
        # change the method by mode
        if args.mode == 'curve':
            plotnow.plots.plot_curve(ax1, dataset, args.colors)
        elif args.mode == 'transition':
            color = next(args.colors)
            ps, xs, ys = plotnow.loader.pick(dataset)
            plotnow.plots.plot_transition(ax1, ax2, ps, xs, ys, color, basename)

    # draw legend 
    if args.legend:
        ax1.legend()
    # limit plot region
    limit_xaxis(ax1, args.xmin, args.xmax)
    limit_yaxis(ax1, args.ymin, args.ymax)
    if args.mode == 'transition':
        limit_yaxis(ax2, args.ymin2, args.ymax2)

    # add labels
    if args.xlabel:
        ax1.set_xlabel(args.xlabel)
    if args.ylabel:
        ax1.set_ylabel(args.ylabel)
    if args.ylabel and args.mode == 'transition':
        ax2.set_ylabel(args.ylabel2)

    # regulate layout
    pl.tight_layout()

    # savefig
    if args.output:
        pl.savefig(args.output, format=args.format)
    else:
        pl.show()

if __name__ == '__main__':
    main()
