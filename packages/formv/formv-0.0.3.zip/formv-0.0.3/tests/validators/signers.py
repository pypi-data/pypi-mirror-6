#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import unittest
from formv.exception import Invalid
from formv.validators.signers import *

class Dummy(object):
    content = 'dummy'

class Test(unittest.TestCase):
    def test(self):
        salt = 'dummy secret'
        dummy = Dummy()
        
        self.assertEqual(None, VSignedString(salt=salt).validate(VSignedString(salt=salt).sign('')))
        self.assertEqual(None, VSignedObject(salt=salt).validate(VSignedObject(salt=salt).sign('')))

        self.assertRaises(Invalid, VSignedString(salt=salt, required=True).validate, 
                          *(VSignedString(salt=salt).sign(''),))
        self.assertRaises(Invalid, VSignedString(salt=salt, required=True, 
                                                min_len=2, max_len=4).validate, 
                          *(VSignedString(salt=salt).sign('dummy'),))
        self.assertRaises(Invalid, VSignedString(salt=salt, 
                                                min_len=2, max_len=4).validate, 
                          *(VSignedString(salt=salt).sign('dummy'),))

        self.assertEqual('dummy', VSignedString(salt=salt).validate(VSignedString(salt=salt).sign('dummy')))
        self.assertEqual(dummy.content, VSignedObject(salt=salt).validate(VSignedObject(salt=salt).sign(dummy)).content)