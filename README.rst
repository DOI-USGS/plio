===============================
Planetary Input / Output
===============================

.. image:: https://badges.gitter.im/USGS-Astrogeology/plio.svg
   :alt: Join the chat at https://gitter.im/USGS-Astrogeology/plio
   :target: https://gitter.im/USGS-Astrogeology/plio?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

.. image:: https://travis-ci.org/USGS-Astrogeology/plio.svg?branch=master
   :target: https://travis-ci.org/USGS-Astrogeology/plio

.. image:: https://coveralls.io/repos/github/USGS-Astrogeology/plio/badge.svg?branch=master 
   :target: https://coveralls.io/github/USGS-Astrogeology/plio?branch=master


A planetary file I/O API

Installation
------------
Installation is unfortunately complicated due to the difficulty in installing GDAL.  These are the steps that have been successfully tested on Linux and OSX.

1. Install Anaconda or Miniconda with Python 3.5
2. Create a new environment to ensure that the installed package is not going to collide with existing packages

   ``conda create --name <somename> python=3``

3. Install ``plio`` with ``conda install -c usgs-astrogeology plio``.
