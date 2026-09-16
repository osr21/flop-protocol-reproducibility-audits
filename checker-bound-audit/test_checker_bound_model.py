import unittest
from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from checker_bound_model import (
    capture_all_three,
    unanimous_false_accept_correlated,
    unanimous_false_accept_independent,
)


class CheckerBoundTests(unittest.TestCase):
    def test_q_cubed_is_capture_probability(self):
        q = Fraction(2, 5)
        self.assertEqual(capture_all_three(q), Fraction(8, 125))

    def test_q_cubed_is_false_accept_bound_only_with_perfect_honest_checkers(self):
        q = Fraction(2, 5)
        self.assertEqual(
            unanimous_false_accept_independent(q, Fraction(0)),
            capture_all_three(q),
        )

    def test_constant_accepting_honest_checkers_break_the_bound(self):
        q = Fraction(2, 5)
        self.assertEqual(
            unanimous_false_accept_independent(q, Fraction(1)),
            Fraction(1),
        )
        self.assertEqual(
            unanimous_false_accept_correlated(q, Fraction(1)),
            Fraction(1),
        )

    def test_partial_independent_false_acceptance_is_strictly_above_q_cubed(self):
        q = Fraction(1, 5)
        epsilon = Fraction(1, 10)
        observed = unanimous_false_accept_independent(q, epsilon)
        self.assertEqual(observed, Fraction(343, 15625))
        self.assertGreater(observed, capture_all_three(q))

    def test_common_mode_failure_is_more_damaging_than_independent_failure(self):
        q = Fraction(1, 5)
        epsilon = Fraction(1, 10)
        independent = unanimous_false_accept_independent(q, epsilon)
        correlated = unanimous_false_accept_correlated(q, epsilon)
        self.assertEqual(independent, Fraction(343, 15625))
        self.assertEqual(correlated, Fraction(67, 625))
        self.assertGreater(correlated, independent)

    def test_invalid_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            capture_all_three(Fraction(-1, 10))
        with self.assertRaises(ValueError):
            unanimous_false_accept_independent(Fraction(1, 2), Fraction(11, 10))


if __name__ == "__main__":
    unittest.main()