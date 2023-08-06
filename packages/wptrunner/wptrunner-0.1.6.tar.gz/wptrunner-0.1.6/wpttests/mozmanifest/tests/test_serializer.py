import unittest

import sys
import os

from cStringIO import StringIO

from .. import parser

class TokenizerTest(unittest.TestCase):
    def setUp(self):
        self.tokenizer = parser.Tokenizer()
