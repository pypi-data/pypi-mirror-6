#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Josh Maine'
__version__ = '1.0.1'
__license__ = 'GPLv3'

import json
from unittest import TestCase
from bit9.bit9_api import Bit9Api, BadCreds, BadDataFormat

USER = 'user'
PASSWORD = 'password'

class InitTests(TestCase):
    def test_bad_creds(self):
        try:
            print 'Bit9 Bad Creds'
            bit9 = Bit9Api()
        except BadCreds:
            pass
        else:
            self.fail('Should have raise a BadCreds Exception')

    def test_bad_data_format(self):
        try:
            print 'Bit9 Bad Data Format'
            bit9 = Bit9Api(USER, PASSWORD, data_format='spaghetti')
        except BadDataFormat:
            pass
        else:
            self.fail('Should have raise a BadDataFormat Exception')

    def test_hash_found(self):
        bit9 = Bit9Api(USER, PASSWORD)

        try:
            print 'Bit9 Usage Info'
            print json.dumps(bit9.lookup_usageinfos, sort_keys=False, indent=4)
        except Exception as e:
            self.fail(e)

    def test_lookup_hashinfo_bad_hash(self):
        bit9 = Bit9Api(USER, PASSWORD)
        try:
            print 'Bit9 Bad Hash'
            print json.dumps(bit9.lookup_hashinfo('A'*32), sort_keys=False, indent=4)
            print json.dumps(bit9.lookup_hashinfo('This is not a hash!!'), sort_keys=False, indent=4)
            print json.dumps(
                bit9.lookup_hashinfo('5e28284f9b5f9097640d58a73d38ad4c5e28284f9b5f9097640d58a73d38ad4c555'),
                sort_keys=False, indent=4)
        except Exception as e:
            self.fail(e)

    def test_lookup_hashinfo_good_hash_md5(self):
        bit9 = Bit9Api(USER, PASSWORD)
        # Win 7 SP1 - calc.exe
        calc_exe_md5 = '60B7C0FEAD45F2066E5B805A91F4F0FC'
        try:
            print 'Bit9 calc.exe md5 Hash'
            print json.dumps(bit9.lookup_hashinfo(calc_exe_md5), sort_keys=False, indent=4)
        except Exception as e:
            self.fail(e)

    def test_lookup_hashinfo_good_hash_sha1(self):
        bit9 = Bit9Api(USER, PASSWORD)
        # Win 7 SP1 - calc.exe
        calc_exe_sha1 = '9018a7d6cdbe859a430e8794e73381f77c840be0'
        try:
            print 'Bit9 calc.exe sha1 Hash'
            print json.dumps(bit9.lookup_hashinfo(calc_exe_sha1), sort_keys=False, indent=4)
        except Exception as e:
            self.fail(e)

    def test_lookup_hashinfo_good_hash_sha256(self):
        bit9 = Bit9Api(USER, PASSWORD)
        # Win 7 SP1 - calc.exe
        calc_exe_sha256 = '80c10ee5f21f92f89cbc293a59d2fd4c01c7958aacad15642558db700943fa22'
        try:
            print 'Bit9 calc.exe sha256 Hash'
            print json.dumps(bit9.lookup_hashinfo(calc_exe_sha256), sort_keys=False, indent=4)
        except Exception as e:
            self.fail(e)


    def test_lookup_hashinfo_hash_list(self):
        bit9 = Bit9Api(USER, PASSWORD)
        test_hashes = ['60B7C0FEAD45F2066E5B805A91F4F0FC',
                       'a31691f0078652207ea0b463342b464f',
                       '5e28284f9b5f9097640d58a73d38ad4c',
                       '60B7C0FEAD45F2066E5B805A91F4F0FD']
        test_hashes_csv = '60B7C0FEAD45F2066E5B805A91F4F0FC,a31691f0078652207ea0b463342b464f,5e28284f9b5f9097640d58a73d38ad4c,60B7C0FEAD45F2066E5B805A91F4F0FD'

        try:
            print 'Bit9 Hash List'
            print json.dumps(bit9.lookup_hashinfo(test_hashes), sort_keys=False, indent=4)
            print json.dumps(bit9.lookup_hashinfo(test_hashes_csv), sort_keys=False, indent=4)
        except Exception as e:
            self.fail(e)

    def test_lookup_hashinfo_hash_mixed_list(self):
        bit9 = Bit9Api(USER, PASSWORD)
        test_mixed_hashes = ['60B7C0FEAD45F2066E5B805A91F4F0FC',
                             '523e506e324da02a28f2588cee6f336ea69590a08651809b4231e1beb5eedba1',
                             '7a90f8b051bc82cc9cadbcc9ba345ced02891a6c']
        try:
            print 'Bit9 Hash Mixed List'
            print json.dumps(bit9.lookup_hashinfo(test_mixed_hashes), sort_keys=False, indent=4)
        except Exception as e:
            self.fail(e)

    def test_lookup_files(self):
        bit9 = Bit9Api(USER, PASSWORD)
        calc_exe_md5 = '60B7C0FEAD45F2066E5B805A91F4F0FC'
        try:
            print 'Bit9 Lookup Files'
            print json.dumps(bit9.lookup_files(calc_exe_md5), sort_keys=False, indent=4)
        except Exception as e:
            self.fail(e)

    def test_lookup_packages(self):
        bit9 = Bit9Api(USER, PASSWORD)
        calc_exe_md5 = '60B7C0FEAD45F2066E5B805A91F4F0FC'
        try:
            print 'Bit9 Lookup Packages'
            print json.dumps(bit9.lookup_packages(calc_exe_md5), sort_keys=False, indent=4)
        except Exception as e:
            self.fail(e)

    def test_lookup_scanresults(self):
        bit9 = Bit9Api(USER, PASSWORD)
        calc_exe_md5 = '60B7C0FEAD45F2066E5B805A91F4F0FC'
        try:
            print 'Bit9 Lookup Scan Results'
            print json.dumps(bit9.lookup_scanresults(calc_exe_md5), sort_keys=False, indent=4)
        except Exception as e:
            self.fail(e)

    def test_lookup_certificates(self):
        bit9 = Bit9Api(USER, PASSWORD)
        calc_exe_md5 = '60B7C0FEAD45F2066E5B805A91F4F0FC'
        try:
            print 'Bit9 Lookup Certificates'
            print json.dumps(bit9.lookup_certificates(calc_exe_md5), sort_keys=False, indent=4)
        except Exception as e:
            self.fail(e)