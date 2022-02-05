import unittest
from wordle_solver import *


zero = (Count.Exact, 0)


class KnowledgeTest(unittest.TestCase):

    def test_build_for_feedback(self):
        self.assertEqual(
            Knowledge.build_for_feedback("kattę", "...!."),
            Knowledge(
                present_on={'t': {3}},
                absent_on={'k': {0}, 'a': {1}, 't': {2}, 'ę': {4}},
                counts={'k': zero, 'a': zero, 't': (Count.Exact, 1), 'ę': zero}))
        self.assertEqual(
            Knowledge.build_for_feedback("tritt", "!..?."),
            Knowledge(
                present_on={'t': {0}},
                absent_on={'r': {1}, 'i': {2}, 't': {3, 4}},
                counts={'r': zero, 'i': zero, 't': (Count.Exact, 2)}))
        self.assertEqual(
            Knowledge.build_for_feedback("dudek", "!.?.!"),
            Knowledge(
                present_on={'d': {0}, 'k': {4}},
                absent_on={'u': {1}, 'd': {2}, 'e': {3}},
                counts={'d': (Count.Min, 2), 'u': zero, 'e': zero, 'k': (Count.Min, 1)}))

    def test_build_for_words(self):
        self.assertEqual(
            Knowledge.build_for_words("kattę", "żółty"),
            Knowledge.build_for_feedback("kattę", "...!."))
        self.assertEqual(
            Knowledge.build_for_words("tritt", "tatko"),
            Knowledge.build_for_feedback("tritt", "!..?."))

    def test_is_possible(self):
        self.assertEqual(
            Knowledge.build_for_feedback("kattę", "...!.").is_possible("żółty"),
            True)


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
