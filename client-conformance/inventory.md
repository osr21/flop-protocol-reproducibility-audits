# Public FLOP task-ID conformance inventory

**Scope:** public, inspectable repositories as of 2026-09-16 UTC. This is an
implementation inventory, not a claim about private code, deployed runtimes,
or an upstream protocol decision. “No path found” means only that the public
revision has no inspectable direct-rail `task_hash`/`report_data` producer or
verifier.

## Canonical acceptance target

The target is the public
[F.1 direct-rail fixture](../hash-wire-audit/evidence/wire-format-v1.json),
pinned to [`flop-labs/yellowpaper` revision
`cb3cbf97a346ff85aca6dba5e924434270ca672c`](https://github.com/flop-labs/yellowpaper/tree/cb3cbf97a346ff85aca6dba5e924434270ca672c).

The harness checks:

- `blake2_256("FLOP/POUI/TASK" || 0x01 || genesis_hash || agent ||
  nonce:u64LE || model_hash || payload_hash || commit_hash)`;
- the 183-byte fixture preimage and task hash
  `8d06cbf826718cda29c2ec2aa363ea13cebc118947eed5fa5d4dbb364357920d`;
- the 145-byte report preimage and 64-byte value
  `SHA256(preimage) || 00×32`; and
- a strict reference-verifier decision that accepts the canonical pair and
  rejects both recorded §1.1-shaped task values (u64LE and u32LE nonce) plus
  bare 32-byte report data.

Run from repository root:

```sh
python3 client-conformance/task_id_conformance.py
python3 -m unittest -v client-conformance/test_task_id_conformance.py
```

The scripts use only the Python standard library.

## Inventory

| Public revision | Inspectable path | Classification | Observed F.1 result |
| --- | --- | --- | --- |
| [`flop-labs/yellowpaper` `cb3cbf97a346`](https://github.com/flop-labs/yellowpaper/tree/cb3cbf97a346ff85aca6dba5e924434270ca672c) | [`evidence/generate-wire-format-vectors.py`](https://github.com/flop-labs/yellowpaper/blob/cb3cbf97a346ff85aca6dba5e924434270ca672c/evidence/generate-wire-format-vectors.py) and [fixture](https://github.com/flop-labs/yellowpaper/blob/cb3cbf97a346ff85aca6dba5e924434270ca672c/evidence/wire-format-v1.json) | Specification, vector corpus, and reference generator; no public runtime client/validator | **Produces the canonical F.1 fixture.** Its generator constructs the domain/version/genesis-bound preimage and 64-byte report value. §1.1 prose remains a conflicting legacy description; see [#61](https://github.com/flop-labs/yellowpaper/issues/61). |
| [`retardio73-boop/flop-conformance-lab` `902317385121`](https://github.com/retardio73-boop/flop-conformance-lab/tree/902317385121fd576e194fd965e0de3471aa8753) | [`src/yellowpaper-61.ts`](https://github.com/retardio73-boop/flop-conformance-lab/blob/902317385121fd576e194fd965e0de3471aa8753/src/yellowpaper-61.ts) and [fixture](https://github.com/retardio73-boop/flop-conformance-lab/blob/902317385121fd576e194fd965e0de3471aa8753/conformance/fixtures/yellowpaper-61-direct-rail-v0.5.0.json) | Downstream conformance harness/reference verifier, not a client or runtime validator | **Source-level fail closed.** It recomputes F.1 and records both legacy values as negative comparators while the source conflict is open. Its all-suite Node test command was not executable in the clean inspection because its dependencies were absent; this is not a test failure claim. |
| [`osr21/flop-protocol-reproducibility-audits` `65ee8779bc85`](https://github.com/osr21/flop-protocol-reproducibility-audits/tree/65ee8779bc855f47c931af2aa1c1684f1a76f9bc) | [`hash-wire-audit/check_hash_wire.py`](../hash-wire-audit/check_hash_wire.py) | Independent audit/reference verifier, not a client | **Pass.** Recomputes F.1 from the public vector and demonstrates the §1.1 divergence. |
| [`osr21/flop-soft-verification-reference` `3fb753305947`](https://github.com/osr21/flop-soft-verification-reference/tree/3fb753305947c578177550c73c32d46ca5b2c3d8) | [SOFT vectors and model](https://github.com/osr21/flop-soft-verification-reference/tree/3fb753305947c578177550c73c32d46ca5b2c3d8) | Independent SOFT state/economic model | **No direct-rail path found.** It does not implement F.1 task construction or report-data verification. |
| [`flop-labs/tclk` `5cc4ab93efbc`](https://github.com/flop-labs/tclk/tree/5cc4ab93efbc8999a3a7e1471b639deca25998ea) | [`tests/vectors.test.ts`](https://github.com/flop-labs/tclk/blob/5cc4ab93efbc8999a3a7e1471b639deca25998ea/tests/vectors.test.ts) | TCLK client/SDK-like protocol and vectors | **No direct-rail path found.** Its `FLOP::tclk::v1` commitments are a separate wire format, not evidence of F.1 compatibility. |
| [`flop-labs/technocore-chat` `542790bdbdc6`](https://github.com/flop-labs/technocore-chat/tree/542790bdbdc6fe8ba30424531159b33711370a59) | Public service, MCP package, and tests | Chat service/client code | **No direct-rail path found.** The public revision has no `task_hash`, `report_data`, or `FLOP/POUI/TASK` construction/verification path. |
| [`flop-labs/technocore-sonnet-challenge` `81761a462bab`](https://github.com/flop-labs/technocore-sonnet-challenge/tree/81761a462bab4d2389e16f995ff9f91688654afc) | [`sonnet_validate.py`](https://github.com/flop-labs/technocore-sonnet-challenge/blob/81761a462bab4d2389e16f995ff9f91688654afc/sonnet_validate.py) | Poem-challenge validator | **No direct-rail path found.** Its validation domain is unrelated to FLOP direct-rail task IDs. |

## Interpretation

The public evidence supports a narrow conclusion:

1. the published F.1 generator and both public conformance harnesses use the
   canonical value and fail closed on the §1.1 conflict;
2. no inspectable public FLOP runtime client, direct-rail validator, or SDK
   was available to certify as accepting or rejecting the legacy form; and
3. therefore no claim can be made about deployed client compatibility or an
   upstream resolution.

The concrete next release gate is to run this harness against every future
public direct-rail producer and verifier, requiring canonical F.1 output and
negative rejection of both legacy task forms and bare 32-byte report data.