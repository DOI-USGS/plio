import os
import numpy as np

# Reads a .atf file and outputs all of the
# .ipf, .gpf, .sup, .prj, and path to locate the
# .apf file (should be the same as all others)
def read_atf(atf_file):
    with open(atf_file) as f:

        files = []
        ipf = []
        sup = []
        files_dict = []

        # Grabs every PRJ, GPF, SUP, and IPF image from the ATF file
        for line in f:
            if line[-4:-1] == 'prj' or line[-4:-1] == 'gpf' or line[-4:-1] == 'sup' or line[-4:-1] == 'ipf' or line[-4:-1] == 'atf':
                files.append(line)

        files = np.array(files)

        # Creates appropriate arrays for certain files in the right format
        for file in files:
            file = file.strip()
            file = file.split(' ')

            # Grabs all the IPF files
            if file[1].endswith('.ipf'):
                ipf.append(file[1])

            # Grabs all the SUP files
            if file[1].endswith('.sup'):
                sup.append(file[1])

            files_dict.append(file)

        # Creates a dict out of file lists for GPF, PRJ, IPF, and ATF
        files_dict = (dict(files_dict))

        # Sets the value of IMAGE_IPF to all IPF images
        files_dict['IMAGE_IPF'] = ipf

        # Sets the value of IMAGE_SUP to all SUP images
        files_dict['IMAGE_SUP'] = sup

        # Sets the value of PATH to the path of the ATF file
        files_dict['PATH'] = os.path.dirname(os.path.abspath(atf_file))

        return files_dict
