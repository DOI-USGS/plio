import os
from setuptools import setup, find_packages

#Grab the README.md for the long description
with open('README.md', 'r') as f:
    long_description = f.read()

def setup_package():
    setup(
        name = "plio",
        version = '1.5.1',
        author = "USGS Astrogeology",
        author_email = "jlaura@usgs.gov",
        description = ("I/O API to support planetary data formats."),
        long_description = long_description,
        license = "Public Domain",
        keywords = "planetary io",
        url = "http://packages.python.org/plio",
        packages=find_packages(),
        include_package_data=True,
        package_data={'plio' : ['sqlalchemy_json/*.py', 'sqlalchemy_json/LICENSE']},
        zip_safe=True,
        scripts=['bin/socetnet2isis', 'bin/isisnet2socet'],
        install_requires=[
            'numpy',
            'pyproj',
            'pvl',
            'h5py',
            'protobuf',
            'pandas',
            'sqlalchemy',
            'pyyaml',
            'networkx',
            'affine',
            'scipy'],
        extras_require={'io_gdal' : "gdal"},
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Topic :: Utilities",
            "License :: Public Domain",
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
        ],
    )

if __name__ == '__main__':
    setup_package()
