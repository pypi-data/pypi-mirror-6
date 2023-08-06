import os
import doctest
from unittest import TestCase, skipUnless

from . import noninteractive, compete, get_source

from .examples import (
    dumb_player, err_divzero, err_syntax, err_badfun, err_oom, err_timeout
)


class NonInteractive(TestCase):
    def test_ok(self):
        ok(self, dumb_player, dumb_player)

    def test_error_x(self):
        assert_error_x(self, *compete(err_divzero, dumb_player))

    def test_error_o(self):
        assert_error_o(self, *compete(dumb_player, err_divzero))

    def test_error_x_syntax(self):
        assert_error_x(self, *compete(err_syntax, dumb_player))

    def test_error_o_syntax(self):
        assert_error_o(self, *compete(dumb_player, err_syntax))

    def test_error_x_badfun(self):
        assert_error_x(self, *compete(err_badfun, dumb_player))

    def test_error_o_badfun(self):
        assert_error_o(self, *compete(dumb_player, err_badfun))

    def test_error_timeout(self):
        compete_res = compete(dumb_player, err_timeout, timeout=0.05)
        r = assert_error_o(self, *compete_res)
        self.assertIn("timeout", r)


@skipUnless(os.path.isdir('/sys/fs/cgroup/memory/tictactoe'), 'no cgroups')
class MemoryTestCase(TestCase):
    def test_error_oom(self):
        onek = 1 << 20  # 1M
        compete_res = compete(dumb_player, err_oom, memlimit=onek)
        r = assert_error_o(self, *compete_res)
        self.assertIn("probably OOM", r)

    def test_mem_x_ok(self):
        twomegs = 1 << 21  # 2M
        ok(self, dumb_player, dumb_player, memlimit=twomegs)

def ok(self, *args, **kwargs):
    ok, state, gameplay = compete(*args, **kwargs)
    self.assertEqual('ok', ok)
    self.assertEqual('o', state)
    self.assertEqual([1, 2, 4, 3], gameplay[:4])
    self.assertNotEqual(0, gameplay[-1])

def assert_error_x(self, error, guilty, reason, gameplay):
    self.assertEqual('error', error)
    self.assertEqual('x', guilty)
    self.assertEqual([0], gameplay)
    return reason

def assert_error_o(self, error, guilty, reason, gameplay):
    self.assertEqual('error', error)
    self.assertEqual('o', guilty)
    self.assertEqual([1, 0], gameplay)
    return reason


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(noninteractive))
    return tests

