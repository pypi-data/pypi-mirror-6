# coding=utf-8
"""
"""
__author__ = 'Alisue <lambdalisue@hashnote.net>'
import os
import numpy as np
import maidenhair
import maidenhair.filters
import maidenhair.statistics


def load(path, recursive, reverse=False, relative=False, using=(0, 1)):
    if os.path.isdir(path):
        # load files (and directories) in the directory
        dataset = []
        for name in os.listdir(path):
            p = os.path.join(path, name)
            if not os.path.isdir(p):
                # load data with maidenhair
                dataset += maidenhair.load(p, using=using, with_filename=True)
            elif recursive:
                # recursively load data in the directory
                dataset += load(p, recursive, reverse, relative, using=using)
    else:
        dataset = maidenhair.load(p, using=using, with_filename=True)
    # post modification, reverse and relative
    if reverse:
        dataset = list(reversed(dataset))
    if relative:
        # dataset contains filename in 1st column, X in 2nd column, and Y in
        # thrid column (column=2).
        dataset = maidenhair.filters.relative(dataset, column=2)
    return dataset

def pick(dataset, where=None):
    """
    Pick curve peak of data
    """
    ps = []; xs = []; ys = []
    for p, x, y in dataset:
        if where:
            # filter values with where function
            i = np.where(where(x, y))
            x = x[i]
            y = y[i]
        xa = maidenhair.statistics.average(x)
        ya = maidenhair.statistics.average(y)
        # find index for maximum Y value
        ix = np.argmax(ya)
        ps.append(p)
        xs.append(x[ix])
        ys.append(y[ix])
    return ps, np.array(xs), np.array(ys)
