'''
    MyKeys key file
    ~~~~~~~~~~~~~~~

    Gets/sets the key file

    :copyright: Copyright 2014 by Vlad Riscutia
    :license: FreeBSD, see LICENSE file
'''
import os
import sys


def get_module_file():
    '''
    Gets the package keyfile
    '''
    return os.path.join(
        os.path.dirname(sys.modules['mykeys'].__file__),
        'data/keyfile')


def get_file():
    '''
    Gets the file in which keys are stored
    '''
    return open(get_module_file(), 'r').read()


def set_file(path):
    '''
    Sets the file in which keys are stored
    '''
    open(get_module_file(), 'w').write(os.path.abspath(path))
    
