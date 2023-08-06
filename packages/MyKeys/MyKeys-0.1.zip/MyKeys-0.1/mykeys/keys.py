'''
    MyKeys Keys object
    ~~~~~~~~~~~~~~~~~~
  
    Generates the object containing the keys extracted from the key file

    :copyright: Copyright 2014 by Vlad Riscutia  
    :license: FreeBSD, see LICENSE file
'''
import configparser
from mykeys import keyfile


class KeySecretPair:
    '''
    Represents a key/secret pair
    '''
    def __init__(self, key="", secret=""):
        self.key = key
        self.secret = secret
    

def parse_keys():
    '''
    Parse keys file
    '''
    keys = configparser.ConfigParser()
    keys.read(keyfile.get_file())

    keys['DEFAULT']['key'] = ""
    keys['DEFAULT']['secret'] = ""

    attributes = dict()
    for section in keys.sections():
        attributes[section] = KeySecretPair(keys[section]['key'], keys[section]['secret'])

    return type('Keys', (), attributes)


Keys = parse_keys()        

