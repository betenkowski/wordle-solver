import unittest
from wordle_solver import *


class MyTestCase(unittest.TestCase):
    def test_report_for_feedback(self):
        self.assertEqual(
            report_for_feedback("kattę", "...!."),
            Report(
                {'k': {0}, 'a': {1}, 't': {2}, 'ę': {4}},
                {'t': {3}},
                {}))
        self.assertEqual(
            report_for_feedback("tritt", "!..?."),
            Report(
                {'r': {1}, 'i': {2}, 't': {4}},
                {'t': {0}},
                {'t': {3}}))

    def test_report_for_words(self):
        self.assertEqual(
            report_for_words("kattę", "żółty"),
            report_for_feedback("kattę", "...!."))
        self.assertEqual(
            report_for_words("tritt", "tatko"),
            report_for_feedback("tritt", "!..?."))

    def test_is_possible_single(self):
        self.assertEqual(
            is_possible_single(report_for_feedback("kattę", "...!."), "żółty"),
            True)


if __name__ == '__main__':
    unittest.main()
