<p align="center">
  <img src="docs/PLIO_Logo.svg" alt="PLIO" width=200> 
</p>

Planetary Input / Output [![Join the chat at https://gitter.im/USGS-Astrogeology/plio](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/USGS-Astrogeology/plio?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
===============================

A planetary surface data input/output library written in Python. The release version of `plio` is avaiable via conda-forge. 

Current build status
====================

[![Linux](https://img.shields.io/circleci/project/github/conda-forge/plio-feedstock/master.svg?label=Linux)](https://circleci.com/gh/conda-forge/plio-feedstock)
[![OSX](https://img.shields.io/travis/conda-forge/plio-feedstock/master.svg?label=macOS)](https://travis-ci.org/conda-forge/plio-feedstock)
[![Windows](https://img.shields.io/appveyor/ci/conda-forge/plio-feedstock/master.svg?label=Windows)](https://ci.appveyor.com/project/conda-forge/plio-feedstock/branch/master)

[![Documentation Status](https://readthedocs.org/projects/plio/badge/?version=latest)](https://plio.readthedocs.io/en/latest/?badge=latest)

Current release info
====================

| Name | Downloads | Version | Platforms |
| --- | --- | --- | --- |
| [![Conda Recipe](https://img.shields.io/badge/recipe-plio-green.svg)](https://anaconda.org/conda-forge/plio) | [![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/plio.svg)](https://anaconda.org/conda-forge/plio) | [![Conda Version](https://img.shields.io/conda/vn/conda-forge/plio.svg)](https://anaconda.org/conda-forge/plio) | [![Conda Platforms](https://img.shields.io/conda/pn/conda-forge/plio.svg)](https://anaconda.org/conda-forge/plio) |

Installing plio
===============

Installing `plio` from the `conda-forge` channel can be achieved by adding `conda-forge` to your channels with:

```
conda config --add channels conda-forge
```

Once the `conda-forge` channel has been enabled, `plio` can be installed with:

```
conda install plio
```

It is possible to list all of the versions of `plio` available on your platform with:

```
conda search plio --channel conda-forge
```

Installing development branch of plio
=====================================

We maintain a development branch of plio that is used as a staging area for our releases. The badges and information below describe the bleeding edge builds.

[![Build Status](https://travis-ci.org/USGS-Astrogeology/plio.svg?branch=dev)](https://travis-ci.org/USGS-Astrogeology/plio)

[![Coverage Status](https://coveralls.io/repos/github/USGS-Astrogeology/plio/badge.svg?branch=master)](https://coveralls.io/github/USGS-Astrogeology/plio?branch=master)


To install the development version: 

```
conda install -c usgs-astrogeology/label/dev plio
```
