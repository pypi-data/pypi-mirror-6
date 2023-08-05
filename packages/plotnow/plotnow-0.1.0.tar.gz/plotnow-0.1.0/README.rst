plotnow
==========================
.. image:: https://pypip.in/d/plotnow/badge.png
    :target: https://pypi.python.org/pypi/plotnow/
    :alt: Downloads

.. image:: https://pypip.in/v/plotnow/badge.png
    :target: https://pypi.python.org/pypi/plotnow/
    :alt: Latest version

.. image:: https://pypip.in/wheel/plotnow/badge.png
    :target: https://pypi.python.org/pypi/plotnow/
    :alt: Wheel Status

.. image:: https://pypip.in/egg/plotnow/badge.png
    :target: https://pypi.python.org/pypi/plotnow/
    :alt: Egg Status

.. image:: https://pypip.in/license/plotnow/badge.png
    :target: https://pypi.python.org/pypi/plotnow/
    :alt: License

A graph plotting application for 2D data.

Installation
------------
Use pip_ like::

    $ pip install plotnow

.. _pip:  https://pypi.python.org/pypi/pip

Usage
------
::

    usage: plotnow [-h] [-r RC_FILE] [--colors COLORS] [--parser PARSER]
                [--loader LOADER] [--recursive] [--reverse] [--relative]
                [-o OUTPUT]
                [-f {pgf,svgz,tiff,jpg,raw,jpeg,png,ps,svg,eps,rgba,pdf,tif}]
                [-m {curve,transition}] [--width WIDTH] [--height HEIGHT]
                [--xlabel XLABEL] [--ylabel YLABEL] [--ylabel2 YLABEL2]
                [--xmin XMIN] [--xmax XMAX] [--ymin YMIN] [--ymax YMAX]
                [--ymin2 YMIN2] [--ymax2 YMAX2] [--without-legend]
                [infiles [infiles ...]]

    positional arguments:
    infiles

    optional arguments:
    -h, --help            show this help message and exit
    -r RC_FILE, --rc-file RC_FILE
                            A filename of matplotlib RC file will be loaded. You
                            can specify the absolute path or relative path. If you
                            specify it with relative path, the relative path from
                            working directory will be used.
    --colors COLORS       A comma separated HTML colors.
    --parser PARSER       A maidenhair parser name.
    --loader LOADER       A maidenhair loader name.
    --recursive           Recursively load data from a directory.
    --reverse             Reverse data loading order.
    --relative            Translate data to relative value to the 1st data
                            loaded.
    -o OUTPUT, --output OUTPUT
                            An output graph file. File type will be automatically
                            detected from the extensions. Or you can specify the
                            file type with --format option.
    -f {pgf,svgz,tiff,jpg,raw,jpeg,png,ps,svg,eps,rgba,pdf,tif}, --format {pgf,svgz,tiff,jpg,raw,jpeg,png,ps,svg,eps,rgba,pdf,tif}
                            An output graph file type.
    -m {curve,transition}, --mode {curve,transition}
                            A mode of plotting. 'curve' is used for plotting
                            relation between X and Y data. 'transition' is used
                            for plotting relation among X1-Xn and Y1-Yn data.
    --width WIDTH         A width in inch of output graph.
    --height HEIGHT       A height in inch of output graph.
    --xlabel XLABEL       A label text of X axis.
    --ylabel YLABEL       A label text of Y axis.
    --ylabel2 YLABEL2     A label text of Y2 axis used in 'transition' mode.
    --xmin XMIN           Limit minimum value of X axis.
    --xmax XMAX           Limit maximum value of X axis.
    --ymin YMIN           Limit minimum value of Y axis.
    --ymax YMAX           Limit maximum value of Y axis.
    --ymin2 YMIN2         Limit minimum value of Y2 axis used in 'transition'
                            mode.
    --ymax2 YMAX2         Limit maximum value of Y2 axis used in 'transition'
                            mode.
    --without-legend      Disable legend drawing.
