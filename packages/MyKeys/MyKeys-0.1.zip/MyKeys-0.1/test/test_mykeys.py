'''
    MyKeys tests
    ~~~~~~~~~~~~
  
    :copyright: Copyright 2014 by Vlad Riscutia  
    :license: FreeBSD, see LICENSE file
'''
from mykeys import cmdline, keyfile, keys
import configparser
import os
import unittest


class TestMyKeys(unittest.TestCase):
    '''
    Unit tests
    '''

    def setUp(self):
        self.save_keyfile = keyfile.get_file()


    def test_command_line(self):
        '''
        Test updating keyfile via command line 
        '''
        cmdline.main(["-f", "dummy"])

        expected = os.path.abspath("dummy")

        self.assertEquals(expected, keyfile.get_file())


    def test_key_file(self):
        '''
        Test get_file/set_file APIs
        '''
        keyfile.set_file("dummy")

        expected = os.path.abspath("dummy")

        self.assertEquals(expected, keyfile.get_file())


    def test_keys(self):
        '''
        Test Keys object
        '''

        # generate test keyfile
        testkeys = configparser.ConfigParser()
        testkeys['test1'] = { 'key': "testkey1", 'secret': "testsecret1" }
        testkeys['test2'] = { 'key': "testkey2" }
        testkeys['test3'] = { 'secret': "testsecret3" }
        testkeys['test4'] = { 'key': "testkey4", 'secret': "testsecret4", 'ignored': "ignored5" }

        TEST_KEYFILE = os.path.join(os.path.dirname(__file__), "testkeyfile")

        with open(TEST_KEYFILE, 'w') as testkeyfile:
            testkeys.write(testkeyfile)

        # set it as keyfile
        keyfile.set_file(TEST_KEYFILE)

        # re-generate Keys object
        keys.Keys = keys.parse_keys()

        self.assertEquals("testkey1", keys.Keys.test1.key)
        self.assertEquals("testsecret1", keys.Keys.test1.secret)
        self.assertEquals("testkey2", keys.Keys.test2.key)
        self.assertEquals("", keys.Keys.test2.secret)
        self.assertEquals("", keys.Keys.test3.key)
        self.assertEquals("testsecret3", keys.Keys.test3.secret)
        self.assertEquals("testkey4", keys.Keys.test4.key)
        self.assertEquals("testsecret4", keys.Keys.test4.secret)

        os.remove(TEST_KEYFILE)

