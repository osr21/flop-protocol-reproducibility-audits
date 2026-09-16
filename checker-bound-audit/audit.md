# Checker-bound audit: what `q³` does and does not establish

**Status:** non-authoritative research audit; not a protocol change or a
measurement of the bonded checker lane.

## Question

Issue [flop-labs/yellowpaper#3](https://github.com/flop-labs/yellowpaper/issues/3)
asks whether R3.5d's statement that an adversary with selection-weight share
`q` captures all three checker seats with probability at most `q³` also
supports a bound on a false unanimous verdict.

This audit reproduces the narrow mathematical distinction. It does **not**
validate the issue's 40% figure as a bonded-lane measurement.

## Normative source and assumptions

The Yellow Paper draft says that three checkers are VRF-assigned, distinct,
and unanimous; disagreement or unavailable evidence escalates and cannot
become an implicit accept. It then says that an adversary with share `q`
captures all three seats with probability at most `q³`
([`yellowpaper.md`, lines 574–591](https://github.com/flop-labs/yellowpaper/blob/main/yellowpaper.md#L574-L591)).
The probability chain later defines `p_effective` as conditional factors,
including `P(upheld | selected, data, challenge, included)`
([lines 593–599](https://github.com/flop-labs/yellowpaper/blob/main/yellowpaper.md#L593-L599)).

For the equality model in this audit, assume:

1. Each of three seats is an independent stake-weighted draw with adversarial
   probability `q` (or a without-replacement mechanism whose all-adversarial
   probability is no larger than that product).
2. An adversarial checker accepts invalid work.
3. A non-adversarial checker independently re-executes and rejects invalid
   work with probability `1 - ε`.
4. The checker verdict is unanimous acceptance.

Assumption 3 is the missing bridge. “Not adversarial” alone does not imply
`ε = 0`, independence, or even that the verdict depends on the work.

## Exact result

`q³` is exactly the probability of **all three seats being adversarial** under
assumption 1. If honest false acceptance is independent across seats with rate
`ε`, the false-unanimous-accept probability is:

```text
(q + (1 - q) ε)^3
```

It reduces to `q³` only when `ε = 0`. If honest failures share a common mode,
the corresponding sensitivity expression is:

```text
q³ + (1 - q³) ε
```

These are model equations, not claims about deployed behavior.

## Counterexample

Let `q = 1/5`. Suppose all checkers, including honest ones, return a constant
`ACCEPT` without making their verdict depend on the work. Then `ε = 1`, and:

```text
P(all seats captured)          = (1/5)^3 = 1/125 = 0.008
P(false unanimous ACCEPT)      = 1
```

The adversary controls no seat in most runs, yet the invalid work is still
accepted. Therefore `q³` cannot by itself bound false acceptance or
`P(upheld | ...)` in the `p_effective` chain.

The weaker non-constant example `q = 1/5`, `ε = 1/10` gives:

```text
independent honest failures: (1/5 + 4/5·1/10)^3 = 343/15625 = 0.021952
common-mode honest failure:   1/125 + (124/125)·1/10 = 67/625 = 0.1072
```

Both exceed `q³ = 0.008`; dependence can make the gap materially larger.

## What the public evidence does and does not show

Issue #3 cites
[`verdict_constancy_census.py`](https://github.com/toma86hawk/technocore-flop-japan/blob/main/verdict_constancy_census.py),
which reports 976 of 2,439 observed ACCEPT verdicts (approximately 40.0%)
reusing a reason across a different job. That is evidence of constant-looking
behavior in the cited board population, not a measurement of `P(upheld)` for
bonded, VRF-assigned R3.5d checkers. The repository itself describes the
census as a mechanical behavioral prior, and issue #3 explicitly disclaims
equating it with the bonded lane.

The local economics note also warns that `q³` captures seat selection, while
the `p_effective` chain needs a separately justified adjudication factor:
[`audit-economics-evidence.md`, lines 34–43 and 92–105](https://github.com/flop-labs/yellowpaper/blob/main/research/audit-economics-evidence.md#L34-L43).

## Conditions under which `q³` is justified

It is a valid upper bound for false unanimous acceptance only if the protocol
or an independently validated measurement establishes all of the following:

* assignment capture really is bounded by `q³` under the deployed weighted
  sampling and distinctness rules;
* every non-captured checker produces a work-dependent verdict;
* for invalid work, each non-captured checker rejects with probability one
  (or a separately published bound proves the resulting aggregate is at most
  `q³`);
* any correlated honest failure, shared model, unavailable evidence, and
  rubber-stamping path is fail-closed rather than an implicit accept; and
* checker bonds, overturn handling, and fresh disjoint escalation assignments
  are enforceable, so later detection is not merely assumed.

Without those conditions, `q³` should be reported as a **capture probability**,
not as a false-verdict or upheld-verdict bound.

## Alternative requirement

Use an explicit checker reliability term. For each attack class and traffic
regime, publish a lower confidence bound for:

```text
P(reject invalid work | checker not adversarial, evidence available)
```

Then compute the resulting unanimous-verdict bound with a stated dependence
model. If that lower bound is zero, the non-TEE lane must not claim
`p_effective > 0` from `q³`; instead require one of:

1. a proof-carrying/work-dependent response (for example, the Freivalds leaf
   value or recomputed activation commitment) before accepting;
2. protocol-funded random re-audits of unanimous accepts; or
3. fail-closed escalation/high-value proof for the affected value class.

These are proposed audit requirements, not a claim that the Yellow Paper has
adopted them.

## Reproduction

From this directory:

```bash
python3 checker_bound_model.py
python3 -m unittest -v test_checker_bound_model.py
```

The model uses exact `fractions.Fraction` arithmetic and no third-party
packages. Expected test result: six passing tests.

## References

* [Issue #3](https://github.com/flop-labs/yellowpaper/issues/3)
* [Yellow Paper §3.5 / R3.5d](https://github.com/flop-labs/yellowpaper/blob/main/yellowpaper.md#35-tier-3--independent-optimistic-re-execution--slashing)
* [Yellow Paper E.45](https://github.com/flop-labs/yellowpaper/blob/main/yellowpaper.md#e45-conditional-economic-safety-profile)
* [Cited census tool](https://github.com/toma86hawk/technocore-flop-japan/blob/main/verdict_constancy_census.py)
* [Local conditional economics evidence](../hash-wire-audit/research/audit-economics-evidence.md)