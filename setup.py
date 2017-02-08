import os
from setuptools import setup, find_packages
import plio
from plio.examples import available
#Grab the README.md for the long description
with open('README.rst', 'r') as f:
    long_description = f.read()


VERSION = plio.__version__

def setup_package():
    examples = set()
    for i in available():
        if not os.path.isdir('plio/examples/' + i):
            if '.' in i:
                glob_name = 'examples/*.' + i.split('.')[-1]
            else:
                glob_name = 'examples/' + i
        else:
            glob_name = 'examples/' + i + '/*'
        examples.add(glob_name)

    setup(
        name = "plio",
        version = VERSION,
        author = "Jay Laura",
        author_email = "jlaura@usgs.gov",
        description = ("I/O API to support planetary data formats."),
        long_description = long_description,
        license = "Public Domain",
        keywords = "planetary io",
        url = "http://packages.python.org/plio",
        packages=find_packages(),
        include_package_data=True,
        package_data={'plio' : list(examples) + ['data/*.db', 'data/*.py'] +\
                ['sqlalchemy_json/*.py', 'sqlalchemy_json/LICENSE']},
        zip_safe=False,
        install_requires=[
            'gdal',
            'numpy',
            'pvl',
            'protobuf==3.0.0b2',
            'h5py',
            'pandas',
            'sqlalchemy',
            'pyyaml',
            'networkx'],
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
