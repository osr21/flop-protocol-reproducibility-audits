# F.1 direct-rail public release scan — 2026-09-17

**Result:** no certifiable public FLOP direct-rail producer, runtime validator,
or SDK was found. This result is time-bounded to the public repositories and
releases inspected below. It says nothing about private repositories, deployed
services, or an upstream protocol decision.

## What this scan required

A qualifying candidate had to contain executable code that constructs or
verifies both:

1. the F.1 direct-rail `task_hash` with the `FLOP/POUI/TASK` domain, version
   byte, `genesis_hash`, and `nonce:u64LE`; and
2. the 64-byte `report_data` value (`SHA256(report_preimage) || 00×32`),
   while rejecting the known §1.1-shaped task forms and bare 32-byte digest.

Specification prose, fixture generators, and conformance harnesses were
recorded, but not treated as client/validator certification.

## Fresh public evidence

| Public source | Revision / release inspected | Result |
| --- | --- | --- |
| [`flop-labs/yellowpaper`](https://github.com/flop-labs/yellowpaper) | [`cb3cbf97a346ff85aca6dba5e924434270ca672c`](https://github.com/flop-labs/yellowpaper/tree/cb3cbf97a346ff85aca6dba5e924434270ca672c); no GitHub releases | Appendix F.1 fixture and generator only. It produces the canonical value but is not a runtime client or validator. The §1.1/F.1 conflict remains open in [#61](https://github.com/flop-labs/yellowpaper/issues/61). |
| [`retardio73-boop/flop-conformance-lab`](https://github.com/retardio73-boop/flop-conformance-lab) | [`902317385121fd576e194fd965e0de3471aa8753`](https://github.com/retardio73-boop/flop-conformance-lab/tree/902317385121fd576e194fd965e0de3471aa8753); `v0.1.5-alpha` | Source-level F.1 conformance harness that fails closed on the source conflict. It is explicitly not a direct-rail producer, client, or runtime validator. |
| [`flop-labs/tclk`](https://github.com/flop-labs/tclk) | [`5cc4ab93efbc8999a3a7e1471b639deca25998ea`](https://github.com/flop-labs/tclk/tree/5cc4ab93efbc8999a3a7e1471b639deca25998ea); `v0.1.0` | TCLK SDK uses a separate commitment format; no F.1 direct-rail task-ID or report-data path. |
| [`flop-labs/technocore-chat`](https://github.com/flop-labs/technocore-chat) | [`542790bdbdc6fe8ba30424531159b33711370a59`](https://github.com/flop-labs/technocore-chat/tree/542790bdbdc6fe8ba30424531159b33711370a59) | Public chat/MCP service; no F.1 direct-rail construction or verification path. |
| [`flop-labs/technocore-sonnet-challenge`](https://github.com/flop-labs/technocore-sonnet-challenge) | [`81761a462bab4d2389e16f995ff9f91688654afc`](https://github.com/flop-labs/technocore-sonnet-challenge/tree/81761a462bab4d2389e16f995ff9f91688654afc) | Poem-challenge validator; no F.1 direct-rail task-ID or report-data path. |

The scan also used GitHub public code/repository search for
`FLOP/POUI/TASK`, `task_hash`, `report_data`, and FLOP direct-rail terms. It
found no additional qualifying public runtime implementation. Public
Technocore client repositories returned by that search are DID/contribution
clients, not direct-rail implementations.

## Reusable release gate

The independent reference verifier remains available in this repository:

```sh
python3 client-conformance/task_id_conformance.py
python3 -m unittest -v client-conformance/test_task_id_conformance.py
```

It verifies the exact F.1 fixture and accepts only the canonical task/report
pair. It rejects the 136-byte and 132-byte §1.1-shaped task forms and bare
32-byte report data. Run it against the first public direct-rail implementation
before claiming client compatibility.