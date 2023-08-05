Hipshot converts a video file into a single image simulating a
long-exposure photograph.

Installation
============

Hipshot requires:

-  Python 2;
-  docopt;
-  NumPy;
-  the FFMPEG libraries; and
-  OpenCV and its Python bindings.

Hipshot consists of a package and a script.

To install them,

::

    gunzip < Hipshot-0.4.1.tar.gz | tar -xf -
    cd Hipshot-0.4.1/
    python setup.py install

or with pip,

::

    pip install hipshot

Usage
=====

The hipshot script takes a single argument: the name of a video
file; and an optional argument given by the option ``--weight``
which specifies the weighing factor for each frame in the sum.

::

    Hipshot - Simulate long-exposure photography

    Usage:
        hipshot <file> [--weight <alpha>]

    Options:
        -w, --weight    Sum frames with the specified weight.
        -v, --version   Print version information.
        -h, --help      Print this help.

Example
=======

The following image was created from the video: `ISS Near
Aurora Borealis <http://www.youtube.com/watch?v=uYBYIhH4nsg>`_.

.. figure:: http://www.eliteraspberries.com/images/iss-borealis.png
   :align: center
   :alt: 


