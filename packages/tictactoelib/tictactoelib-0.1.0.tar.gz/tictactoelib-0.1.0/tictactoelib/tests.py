import unittest
import doctest

from . import noninteractive, compete, get_source

from .examples import dumb_player, err_divzero, err_syntax, err_badfun


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(noninteractive))
    return tests


class NonInteractive(unittest.TestCase):
    def test_ok(self):
        ok, state, gameplay = compete(dumb_player, dumb_player)
        self.assertEqual('ok', ok)
        self.assertEqual('o', state)
        self.assertEqual([1, 2, 4, 3], gameplay[:4])
        self.assertNotEqual(0, gameplay[-1])

    def _assert_error_x(self, error, guilty, reason, gameplay):
        self.assertEqual('error', error)
        self.assertEqual('x', guilty)
        self.assertEqual([0], gameplay)

    def _assert_error_o(self, error, guilty, reason, gameplay):
        self.assertEqual('error', error)
        self.assertEqual('o', guilty)
        self.assertEqual([1, 0], gameplay)

    def test_error_x(self):
        self._assert_error_x(*compete(err_divzero, dumb_player))

    def test_error_o(self):
        self._assert_error_o(*compete(dumb_player, err_divzero))

    def test_error_x_syntax(self):
        self._assert_error_x(*compete(err_syntax, dumb_player))

    def test_error_o_syntax(self):
        self._assert_error_o(*compete(dumb_player, err_syntax))

    def test_error_x_badfun(self):
        self._assert_error_x(*compete(err_badfun, dumb_player))

    def test_error_o_badfun(self):
        self._assert_error_o(*compete(dumb_player, err_badfun))
