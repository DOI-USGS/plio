import os
from setuptools import setup, find_packages

#Grab the README.md for the long description
with open('README.md', 'r') as f:
    long_description = f.read()

def setup_package():
    setup(
        name = "plio",
        version = '1.1.0',
        author = "Jay Laura",
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
            'gdal',
            'numpy',
            'pyproj',
            'jinja2',
            'pvl',
            'protobuf',
            'h5py',
            'pandas',
            'sqlalchemy',
            'pyyaml',
            'networkx',
            'affine',
            'scipy'],
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Topic :: Utilities",
            "License :: Public Domain",
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
        ],
    )

if __name__ == '__main__':
    setup_package()
