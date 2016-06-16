from setuptools import setup, find_packages
import plio
#Grab the README.md for the long description
with open('README.rst', 'r') as f:
    long_description = f.read()


VERSION = plio.__version__

def setup_package():

    #import plio
    #print(plio.examples.available())

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
        zip_safe=False,
        install_requires=[
            'gdal>=2',
            'pvl',
            'protobuf==3.0.0b2',
            'h5py',
            'pandas',
            'sqlalchemy',
            'pyyaml'],
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