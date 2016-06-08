from setuptools import setup

setup(
    name = "plio",
    version = "0.1.0",
    author = "Jay Laura",
    author_email = "jlaura@usgs.gov",
    description = ("I/O API to support planetary data formats."),
    license = "Public Domain",
    keywords = "planetary io",
    url = "http://packages.python.org/plio",
    packages=['plio'],
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
