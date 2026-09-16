"""Small exact-probability model for the R3.5d q^3 claim.

The model deliberately separates seat capture from a checker making a
work-dependent decision.  It uses only the Python standard library.
"""

from fractions import Fraction


def capture_all_three(q: Fraction) -> Fraction:
    """Probability that three independent seats are adversarial."""
    _check_probability(q)
    return q**3


def unanimous_false_accept_independent(
    q: Fraction, honest_false_accept: Fraction
) -> Fraction:
    """False unanimous ACCEPT when honest seats fail independently.

    Each seat is adversarial with probability q.  An adversarial checker
    accepts invalid work, while an honest checker accepts invalid work with
    probability ``honest_false_accept``.  This is *not* the default protocol
    model; it is an explicit sensitivity model.
    """
    _check_probability(q)
    _check_probability(honest_false_accept)
    per_seat_accept = q + (1 - q) * honest_false_accept
    return per_seat_accept**3


def unanimous_false_accept_correlated(
    q: Fraction, honest_false_accept: Fraction
) -> Fraction:
    """False unanimous ACCEPT when honest verdicts share one common failure.

    With probability q^3 all seats are adversarial.  Otherwise at least one
    honest checker is present, and a common-mode honest failure causes every
    honest checker to accept with probability ``honest_false_accept``.
    """
    _check_probability(q)
    _check_probability(honest_false_accept)
    return q**3 + (1 - q**3) * honest_false_accept


def _check_probability(value: Fraction) -> None:
    if not 0 <= value <= 1:
        raise ValueError("probabilities must lie in [0, 1]")


if __name__ == "__main__":
    q = Fraction(1, 5)
    print("q =", q)
    print("capture_all_three =", capture_all_three(q))
    print(
        "independent honest false-accept=0 =",
        unanimous_false_accept_independent(q, Fraction(0)),
    )
    print(
        "correlated constant-accept honest failure=1 =",
        unanimous_false_accept_correlated(q, Fraction(1)),
    )