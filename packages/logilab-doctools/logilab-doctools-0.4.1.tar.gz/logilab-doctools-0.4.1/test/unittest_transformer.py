"""
unit tests for the transformer module
"""

from logilab.common.testlib import TestCase, unittest_main
from logilab.doctools.transformer import guess_format, InputGuessException


class GuessformatFunctionTest(TestCase):
    def test_known_values_1(self):
        self.assertEqual(guess_format('machin.txt'), 'rest')

    def test_known_values_2(self):
        self.assertEqual(guess_format('machin.rst'), 'rest')

    def test_known_values_3(self):
        self.assertEqual(guess_format('machin.rest'), 'rest')

    def test_known_values_4(self):
        self.assertEqual(guess_format('machin.xml'), 'docbook')

    def test_known_values_5(self):
        self.assertEqual(guess_format('machin.dbk'), 'docbook')

    def test_known_values_6(self):
        self.assertEqual(guess_format('machin.fo'), 'fo')

    def test_known_values_6(self):
        self.assertEqual(guess_format('bill.xml'), 'pybill')

    def test_raise_1(self):
        self.assertRaises(InputGuessException, guess_format, 'machin.unk')

if __name__ == '__main__':
    unittest_main()
