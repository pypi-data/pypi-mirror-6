# coding=utf-8
"""
"""
__author__ = 'Alisue <lambdalisue@hashnote.net>'
import os
import numpy as np
import maidenhair.statistics
import matplotlib as mpl
import matplotlib.pyplot as pl

def make_label(path):
    """
    Remove extension and dirname from path to make a label
    """
    return os.path.splitext(os.path.basename(path))[0]


def plot_curve(ax, dataset, color_cycle, **opts):
    for (path, x, y), color in zip(dataset, color_cycle):
        xa = maidenhair.statistics.average(x)
        ya = maidenhair.statistics.average(y)
        l = make_label(path)
        ax.plot(xa, ya, color=color, label=l, **opts)


def plot_transition(ax1, ax2, ps, xs, ys, color, label, **opts):
    background = mpl.rcParams['axes.facecolor']
    xx = np.arange(0, len(ps))
    xa = maidenhair.statistics.average(xs)
    ya = maidenhair.statistics.average(ys)


    ax2.plot(xx, xa, color=color,
             linestyle='--', **opts)
    ax1.plot(xx, ya, color=color, label=label,
             linewidth=2,
             marker='o',
             markersize=6,
             markeredgewidth=2,
             markeredgecolor=color,
             markerfacecolor=background)

    ax1.set_xticks(xx)
    ax1.set_xticklabels([make_label(p) for p in ps])

    # rotate xtick labels
    pl.gcf().autofmt_xdate()
