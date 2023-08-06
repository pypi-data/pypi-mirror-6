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

    def test_context_no_leak_alternate_system_tempdir(self):
        import os
        class Foo(object):
            pass
        drippy = self._makeOne()
        log = []
        with _Monkey_tempfile_tempdir() as alternate:
            _before, _while = alternate
            drippy._logout = log.append
            drippy.startContext(Foo)
            not_a_leak = os.path.join(_before, 'tmp_not_a_leak')
            with open(not_a_leak, 'w') as f:
                f.write('NOT A LEAK')
            try:
                drippy.stopContext(Foo)
            finally:
                os.remove(not_a_leak)
        self.assertEqual(len(log), 0)
        self.assertEqual(len(drippy._stack), 0)

    def test_context_w_leak(self):
        from tempfile import NamedTemporaryFile
        class Foo(object):
            pass
        drippy = self._makeOne()
        log = []
        drippy._logout = log.append
        drippy.startContext(Foo)
        leaky = NamedTemporaryFile()
        try:
            drippy.stopContext(Foo)
        finally:
            leaky.close()
        self.assertEqual(len(log), 1)
        self.assertEqual(len(drippy._stack), 0)

    def test_context_w_leak_alternate_system_tempdir(self):
        import os
        class Foo(object):
            pass
        drippy = self._makeOne()
        log = []
        drippy._logout = log.append
        with _Monkey_tempfile_tempdir() as alternate:
            _before, _while = alternate
            drippy.startContext(Foo)
            is_a_leak = os.path.join(_while, 'tmp_is_a_leak')
            with open(is_a_leak, 'w') as f:
                f.write('IS A LEAK')
            try:
                drippy.stopContext(Foo)
            finally:
                os.remove(is_a_leak)
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

    def test_single_test_no_leak_alternate_system_tempdir(self):
        import os
        drippy = self._makeOne()
        log = []
        drippy._logout = log.append
        with _Monkey_tempfile_tempdir() as alternate:
            _before, _while = alternate
            drippy.beforeTest('foo')
            not_a_leak = os.path.join(_before, 'tmp_not_a_leak')
            with open(not_a_leak, 'w') as f:
                f.write('NOT A LEAK')
            try:
                drippy.afterTest('foo')
            finally:
                os.remove(not_a_leak)
        self.assertEqual(len(log), 0)
        self.assertEqual(drippy._test_count, None)

    def test_single_test_w_leak(self):
        from tempfile import NamedTemporaryFile
        drippy = self._makeOne()
        log = []
        drippy._logout = log.append
        drippy.beforeTest('foo')
        leaky = NamedTemporaryFile()
        try:
            drippy.afterTest('foo')
        finally:
            leaky.close()
        self.assertEqual(len(log), 1)
        self.assertEqual(drippy._test_count, None)

    def test_single_test_w_leak_alternate_system_tempdir(self):
        import os
        drippy = self._makeOne()
        log = []
        drippy._logout = log.append
        with _Monkey_tempfile_tempdir() as alternate:
            _before, _while = alternate
            drippy.beforeTest('foo')
            is_a_leak = os.path.join(_while, 'tmp_is_a_leak')
            with open(is_a_leak, 'w') as f:
                f.write('IS A LEAK')
            try:
                drippy.afterTest('foo')
            finally:
                os.remove(is_a_leak)
        self.assertEqual(len(log), 1)
        self.assertEqual(drippy._test_count, None)


class _Monkey_tempfile_tempdir(object):

    def __init__(self, replace='drippy'):
        import tempfile
        self._before = tempfile.tempdir
        tempfile.tempdir = self._while = tempfile.mkdtemp(prefix=replace)

    def __enter__(self):
        return self._before, self._while

    def __exit__(self, *args):
        import shutil
        import tempfile
        tempfile.tempdir = self._before
        shutil.rmtree(self._while)
