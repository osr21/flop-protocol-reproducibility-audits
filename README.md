# FLOP protocol reproducibility audits

Independent, non-authoritative reproducibility audits for public FLOP Yellow Paper reports. These materials identify implementation divergence and security-model boundaries; they do not amend the FLOP protocol or claim upstream adoption.

## Included audits

- [Hash/wire interoperability audit](hash-wire-audit/audit.md) — reproduces the §1.1 versus Appendix F.1 `task_hash` and `report_data` divergence raised in [upstream issue #61](https://github.com/flop-labs/yellowpaper/issues/61).
- [Public client conformance inventory](client-conformance/inventory.md) — checks every inspectable public FLOP-related implementation path against the F.1 fixture and records where no direct-rail implementation is public.
- [Checker-bound audit](checker-bound-audit/audit.md) — distinguishes `q³` all-seat capture from false unanimous acceptance for [upstream issue #3](https://github.com/flop-labs/yellowpaper/issues/3).

## Reproduce

```bash
python3 hash-wire-audit/check_hash_wire.py
python3 -m unittest -v client-conformance/test_task_id_conformance.py
python3 -m unittest -v checker-bound-audit/test_checker_bound_model.py
```

Both use only the Python standard library. The hash/wire audit includes the exact public wire fixture it consumes.

## Scope

The source document is the public FLOP Yellow Paper v0.5.0 mirror. These audits preserve the distinction between a reproducible counterexample and an adopted protocol decision. See the linked upstream issues for review and disposition.

## License

MIT. See [LICENSE](LICENSE).