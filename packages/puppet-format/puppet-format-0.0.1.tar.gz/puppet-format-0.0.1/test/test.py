#!/usr/bin/env python

import re
import os
import sys
import unittest

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "../")))
import puppet

class TestBasic(unittest.TestCase):
    pass

if __name__ == "__main__":
    import sys
    unittest.main()
