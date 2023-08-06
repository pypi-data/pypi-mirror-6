import unittest

class DrippyTests(unittest.TestCase):

    def _getTargetClass(self):
        from drippy import Drippy
        return Drippy

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_context_no_leak(self):
        class Foo(object):
            pass
        drippy = self._makeOne()
        log = []
        drippy._logout = log.append
        drippy.startContext(Foo)
        drippy.stopContext(Foo)
        self.assertEqual(len(log), 0)
        self.assertEqual(len(drippy._stack), 0)

    def test_context_w_leak(self):
        from shutil import rmtree
        from tempfile import mkdtemp
        class Foo(object):
            pass
        drippy = self._makeOne()
        log = []
        drippy._logout = log.append
        drippy.startContext(Foo)
        tempdir = mkdtemp()
        try:
            drippy.stopContext(Foo)
        finally:
            rmtree(tempdir)
        self.assertEqual(len(log), 1)
        self.assertEqual(len(drippy._stack), 0)

    def test_single_test_no_leak(self):
        drippy = self._makeOne()
        log = []
        drippy._logout = log.append
        drippy.beforeTest('foo')
        drippy.afterTest('foo')
        self.assertEqual(len(log), 0)
        self.assertEqual(drippy._test_count, None)

    def test_single_test_w_leak(self):
        from shutil import rmtree
        from tempfile import mkdtemp
        drippy = self._makeOne()
        log = []
        drippy._logout = log.append
        drippy.beforeTest('foo')
        tempdir = mkdtemp()
        try:
            drippy.afterTest('foo')
        finally:
            rmtree(tempdir)
        self.assertEqual(len(log), 1)
        self.assertEqual(drippy._test_count, None)

