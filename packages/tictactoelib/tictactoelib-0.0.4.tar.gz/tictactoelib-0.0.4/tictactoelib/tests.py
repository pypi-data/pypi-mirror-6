import unittest
import doctest

from . import noninteractive, compete, get_source

from .examples import player1, err_syntax


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(noninteractive))
    return tests


class NonInteractive(unittest.TestCase):
    def test_ok(self):
        ok, state, gameplay = compete(player1, player1)
        self.assertEqual('ok', ok)
        self.assertEqual('o', state)
        self.assertEqual([1, 2, 4, 3], gameplay[:4])
        self.assertNotEqual(0, gameplay[-1])

    def test_error_x(self):
        error, reason, gameplay = compete(err_syntax, player1)
        self.assertEqual('error', error)
        self.assertRegex(reason, '^\[string.*')
        self.assertEqual([0], gameplay)

    def test_error_o(self):
        error, reason, gameplay = compete(player1, err_syntax)
        self.assertEqual('error', error)
        self.assertEqual([1, 0], gameplay)
