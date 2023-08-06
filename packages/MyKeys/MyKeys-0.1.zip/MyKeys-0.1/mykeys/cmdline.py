'''
    MyKeys command line
    ~~~~~~~~~~~~~~~~~~~

    Command line to retrieve/update file containing keys

    :copyright: Copyright 2014 by Vlad Riscutia
    :license: FreeBSD, see LICENSE file
'''
import argparse
import os
from mykeys import keyfile


def main(argv=None):
    '''
    Parses command line
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', nargs=1, help="specify keys file")

    command = parser.parse_args(argv)
    
    if command.file:
        keyfile.set_file(command.file[0])
    else:
        print("MyKeys key file: %s" % (keyfile.get_file(), ))

    if not os.path.exists(keyfile.get_file()):
        print("Warning: keyfile not found")

