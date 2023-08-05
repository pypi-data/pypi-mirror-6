===============
yt.formula.node
===============

.. image:: https://travis-ci.org/toumorokoshi/yt.formula.node.png
   :alt: build status
   :target: https://travis-ci.org/toumorokoshi/yt.formula.node

yt.formula.node is a `sprinter <http://github.com/toumorokoshi/sprinter>`_ formula for installing node.js executables and npm packages

Example usage
-------------


.. code::

    [node]
    formula = yt.formula.node:git+https://github.com/toumorokoshi/yt.formula.node.git
    version = 0.10.16
    packages =
      grunt-cli



Options
-------

* version: the version of node you want to install (in the format of X.X.X)
* packages: the npm packages you want to install

All intalled executables are automatically symlinked to your path.
