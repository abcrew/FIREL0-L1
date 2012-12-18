#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Master test suite for FIRE codes

"""

try:
    import unittest_pretty as ut
except ImportError:
    import unittest as ut

from test_FIRE_L0_L1 import *
# add others here as they are written

if __name__ == '__main__':
    ut.main()
