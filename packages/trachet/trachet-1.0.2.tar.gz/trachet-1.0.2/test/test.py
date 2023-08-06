#!/usr/bin/env python
# -*- coding:utf-8
import unittest


class TestSample(unittest.TestCase):

    def test_sample(self):
        self.assertEqual(15, 10 + 5))

    def suite():
        suite = unittest.TestSuite()
        suite.addTests(unittest.makeSuite(TestSample))
        return suite
