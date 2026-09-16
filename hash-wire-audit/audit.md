# Hash/wire audit for GitHub issue #61

**Repository snapshot:** `flop-labs/yellowpaper` at
`cb3cbf97a346ff85aca6dba5e924434270ca672c` (shallow clone, 2026-09-16
working tree snapshot).

## Finding

The prose summary in §1.1 and the normative Appendix F.1/wire corpus do not
describe the same `task_hash` preimage.  The same mismatch propagates into
`report_data` because the latter includes `task_hash`, and the prose also
omits the fixed-width output format required by F.1.

### Exact citations

* `yellowpaper.md:170-172` (§1.1 symbol table) says:
  * `report_data = SHA256(task_hash ‖ gn_weight ‖ latency_ms ‖ model_hash ‖
    output_hash ‖ decode_policy_hash ‖ tee_type)`;
  * `task_hash = blake2_256(agent ‖ nonce ‖ model_hash ‖ payload_hash ‖
    commit_hash)`.
* `yellowpaper.md:2656-2666` (Appendix F.1) defines the v1 task preimage as
  `blake2_256("FLOP/POUI/TASK" ‖ 01 ‖ genesis_hash:H256 ‖ agent:AccountId32
  ‖ nonce:u64LE ‖ model_hash ‖ payload_hash ‖ commit_hash)` and defines
  `report_data` as the SHA-256 digest of fixed-width little-endian fields plus
  `SCALE(tee_type)`, followed by `00×32`, for exactly 64 bytes.
* `evidence/wire-format-v1.json:254-255` records the current 64-byte
  `report_data` and its 145-byte preimage.
* `evidence/wire-format-v1.json:256-273` records the current task inputs,
  v1 preimage, and v1 hash.
* `evidence/generate-wire-format-vectors.py:150-172` is the executable vector
  construction: it includes the domain/version/genesis fields in the task
  preimage, uses `u64LE` fields and a one-byte SCALE tee tag, hashes the
  report preimage, and appends 32 zero bytes.

## Reproduction

Run:

```sh
cd .local/conversation-workspace/files/flop-protocol-audits/hash-wire-audit
python3 check_hash_wire.py
```

The checker reads the published JSON vector and computes both profiles using
only Python's standard library.  For the corpus fixture it reports:

| Profile | Preimage | Digest |
|---|---:|---|
| §1.1 task (literal field concatenation) | 136 bytes | `9ae6090bc6b2b21caa773820ec2802e22bedde93729b3b6ac42e0d78892f6a0d` |
| F.1 task v1 | 183 bytes | `8d06cbf826718cda29c2ec2aa363ea13cebc118947eed5fa5d4dbb364357920d` |
| §1.1 report compatibility candidate* | 145 bytes | `10b0c2222ec2cdf4fada195142155e1a3c0249392c56462fe0b8ef4462822b3a` |
| F.1 report v1 | 145 bytes, then 32-byte pad | `3165c6d38fbf992485c8c8640476f9a7a5db94523a32387e838d205d178bfff7` |

The `*` candidate uses the only directly testable wire interpretation of the
underspecified §1.1 report expression: `u64LE` for the two integers and the
one-byte `SCALE` tag used by F.1.  §1.1 does not itself specify those encodings,
which is an additional interoperability ambiguity.  The candidate is shown
to demonstrate that even with those favorable assumptions, replacing the task
hash changes the report digest.  The F.1 vector's `report_data` is 64 bytes;
the prose expression alone specifies only a 32-byte SHA-256 digest.

## Concrete implementation outcomes

1. A producer implementing the §1.1 task expression emits
   `9ae609…f6a0d` for the corpus inputs; a validator enforcing F.1 expects
   `8d06cb…7920d`.  The validator therefore rejects the producer's
   attestation or indexes the work under a different replay key.
2. A producer/verifier that treats `report_data` as the raw 32-byte SHA-256
   digest emits `10b0c2…2b3a` under the compatibility candidate and supplies
   32 bytes, while the F.1 quote binding expects the `3165c6…fff7` digest
   followed by 32 zero bytes.  A TEE quote verifier checking the 64-byte
   field rejects the shorter or differently bound value.

These are protocol-level divergence outcomes, not merely editorial
differences: `task_hash` is used as the replay/credit identity
(`yellowpaper.md:2668-2679`), and report-data verification is required before
credit (`yellowpaper.md:608-618`).

## Recommendation

Make Appendix F.1 the single normative definition and update §1.1 to match it
verbatim, including:

1. the `"FLOP/POUI/TASK" || 0x01 || genesis_hash` domain/version/deployment
   binding;
2. `u64LE` encoding for `nonce`, `gn_weight`, and `latency_ms`;
3. `SCALE(tee_type)` encoding; and
4. `SHA256(preimage) || 00×32` as the 64-byte `report_data` value.

Add a cross-reference from §1.1 to F.1 and retain the published vector as a
conformance fixture.  Until this edit is made, implementations should reject
or gate the legacy §1.1 profile rather than silently accepting both hashes.
