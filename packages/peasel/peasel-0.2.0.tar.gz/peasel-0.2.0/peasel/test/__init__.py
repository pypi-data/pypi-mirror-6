import unittest

modules = ['test_ceasel']

def suite():
    s = unittest.TestSuite()
    for m in modules:
        module = __import__(__name__ + '.' + m, fromlist=m)
        s.addTests(module.suite())

    return s
