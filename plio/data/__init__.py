import os


def get_data(filename):
    packagedir, _ = os.path.split(__file__)
    fullname = os.path.join(packagedir, filename)
    return fullname