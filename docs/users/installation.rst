Installation
============

We provide Planetary I/O (plio) as a binary package via conda and for
installation via the standard setup.py script.

Via Conda
---------

1. Download and install the Python 3.x Miniconda installer.  Respond ``Yes`` when
   prompeted to add conda to your BASH profile.
2. Bring up a command line and add the ``conda-forge`` channel to your channel
   list: ``conda config --add channels conda-forge``.  This adds an entry to your
   ``~/.condarc`` file.
3. Install plio: ``conda install -c jlaura plio``
4. To update plio: ``conda update -c jlaura plio``

Via setup.py
------------
This method assumes that you have the necessary dependencies already
installed. The installation of dependencies can be non-trivial because of GDAL.
We supply an ``environment.yml`` file that works with Anaconda Python's ``conda
env`` environment management tool.   
