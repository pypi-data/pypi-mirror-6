GlesPy Package Documentation
============================

This package contains line bindings for
`GLESP <http://www.glesp.nbi.dk/>`__ with some 'candies':

Installation
------------

Requirements
~~~~~~~~~~~~

-  `GLESP <http://www.glesp.nbi.dk/>`__ must be installed with all
   dependences for normal work;
-  `numpy <http://numpy.org>`__ to work with dl$
-  `eog <https://projects.gnome.org/eog/>`__ (to show maps).

Installation
~~~~~~~~~~~~

To install package just input to command line:

::

    pip install glespy

Using
-----

To use in python you need to import glespy package

::

    import glespy

Features
--------

Automated parameters control, i.e.:

::

    lmin >= 0
    lmax >= lmin
    nx >= lmax * 2 + 1
    np >= nx * 2

PixelMap
~~~~~~~~

Class for `GLESP <http://www.glesp.nbi.dk/>`__ fits pixel maps. Possible
operations are:

-  arithmetics (+, -, \*, ...);
-  convert from alm `GLESP <http://www.glesp.nbi.dk/>`__ files;
-  draw map (with `eog <https://projects.gnome.org/eog/>`__, if it's
   installed);
-  get map attributes;
-  cut/keep zones;
-  reflect map;
-  mask map;
-  get C(l), alm and gif.

Alm
~~~

Class for `GLESP <http://www.glesp.nbi.dk/>`__ fits alm. Operations:

-  get attributes;
-  convert to `GLESP <http://www.glesp.nbi.dk/>`__ pixel map;
-  smooth;
-  rotate;
-  get C(l).

PointSource
~~~~~~~~~~~

Class for getting `GLESP <http://www.glesp.nbi.dk/>`__ fits map from
file with ascii values. It can be with point sources or pixel map in
ascii format. Operations:

-  get pixel map;
-  show.

Cl
~~

Class for manipulating with angular power spectrum. Operations:

-  convert to alm;
-  convert to pixel map.

Changes
-------

0.1.7.2
~~~~~~~

-  Dl data type now is float32 from numpy

0.1.7.1
~~~~~~~

-  Calculation of D() from alm and pixelmap

0.1.7
~~~~~

-  Class for power spectrum added

0.1.6.1
~~~~~~~

-  description updated

0.1.6
~~~~~

-  quick update alm lmax and lmin
-  temp maps and alm\`s autoremove
-  pointsource can be made of asci file from/for pixelmap
-  python2.6 particle compatibility

