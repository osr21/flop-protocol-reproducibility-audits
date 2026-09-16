#!/usr/bin/env python3
"""Strict, dependency-free F.1 task_id and report_data conformance harness.

This validates the published direct-rail v1 fixture.  It is a reference
verifier, not a FLOP runtime client, validator, signer, or protocol decision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


DOMAIN = b"FLOP/POUI/TASK"
VERSION = b"\x01"
H256_BYTES = 32
REPORT_DATA_BYTES = 64
DEFAULT_VECTOR = (
    Path(__file__).resolve().parent / "evidence" / "direct-rail-v1.json"
)


def _h256_hex(value: str, field: str) -> bytes:
    try:
        decoded = bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    if len(decoded) != H256_BYTES:
        raise ValueError(f"{field} must be exactly 32 bytes")
    return decoded


def _u64(value: Any, field: str) -> bytes:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{field} must be an integer")
    if not 0 <= value <= (2**64 - 1):
        raise ValueError(f"{field} must fit in u64")
    return value.to_bytes(8, "little")


def task_preimage_v1(task: Mapping[str, Any]) -> bytes:
    """Encode the sole accepted Appendix F.1 v1 task preimage."""
    return b"".join(
        (
            DOMAIN,
            VERSION,
            _h256_hex(str(task["genesis_hash_hex"]), "genesis_hash_hex"),
            _h256_hex(str(task["agent_account_id32_hex"]), "agent_account_id32_hex"),
            _u64(task["nonce"], "nonce"),
            _h256_hex(str(task["model_hash_hex"]), "model_hash_hex"),
            _h256_hex(str(task["payload_hash_hex"]), "payload_hash_hex"),
            _h256_hex(str(task["commit_hash_hex"]), "commit_hash_hex"),
        )
    )


def task_hash_v1(task: Mapping[str, Any]) -> bytes:
    return hashlib.blake2b(task_preimage_v1(task), digest_size=H256_BYTES).digest()


def report_preimage_v1(report: Mapping[str, Any]) -> bytes:
    """Encode the F.1 report preimage before its required zero padding."""
    tee_type = report["tee_type"]
    if not isinstance(tee_type, Mapping):
        raise ValueError("tee_type must be an object")
    scale_tag = tee_type["scale_tag"]
    if not isinstance(scale_tag, int) or isinstance(scale_tag, bool):
        raise ValueError("tee_type.scale_tag must be an integer")
    if not 0 <= scale_tag <= 255:
        raise ValueError("tee_type.scale_tag must fit in one byte")
    return b"".join(
        (
            _h256_hex(str(report["task_hash_hex"]), "task_hash_hex"),
            _u64(report["gn_weight"], "gn_weight"),
            _u64(report["latency_ms"], "latency_ms"),
            _h256_hex(str(report["model_hash_hex"]), "model_hash_hex"),
            _h256_hex(str(report["output_hash_hex"]), "output_hash_hex"),
            _h256_hex(
                str(report["decode_policy_hash_hex"]), "decode_policy_hash_hex"
            ),
            bytes((scale_tag,)),
        )
    )


def report_data_v1(report: Mapping[str, Any]) -> bytes:
    return hashlib.sha256(report_preimage_v1(report)).digest() + (b"\0" * H256_BYTES)


def matches_canonical_v1(
    task: Mapping[str, Any],
    report: Mapping[str, Any],
    candidate_task_hash_hex: str,
    candidate_report_data_hex: str,
) -> bool:
    """Return whether a candidate exactly matches the F.1 v1 binding.

    Invalid lengths or hexadecimal are rejected as ``False`` rather than
    admitted through an alternate compatibility interpretation.
    """
    try:
        candidate_task_hash = _h256_hex(
            candidate_task_hash_hex, "candidate_task_hash_hex"
        )
        candidate_report_data = bytes.fromhex(candidate_report_data_hex)
    except ValueError:
        return False
    if len(candidate_report_data) != REPORT_DATA_BYTES:
        return False
    expected_task_hash = task_hash_v1(task)
    expected_report = dict(report)
    expected_report["task_hash_hex"] = expected_task_hash.hex()
    return (
        candidate_task_hash == expected_task_hash
        and candidate_report_data == report_data_v1(expected_report)
    )


def legacy_task_hash(task: Mapping[str, Any], nonce_bytes: int = 8) -> bytes:
    """Return a §1.1-shaped negative comparator; never use it for acceptance."""
    if nonce_bytes not in (4, 8):
        raise ValueError("legacy nonce width must be 4 or 8")
    nonce = task["nonce"]
    if not isinstance(nonce, int) or isinstance(nonce, bool):
        raise ValueError("nonce must be an integer")
    return hashlib.blake2b(
        b"".join(
            (
                _h256_hex(str(task["agent_account_id32_hex"]), "agent_account_id32_hex"),
                nonce.to_bytes(nonce_bytes, "little"),
                _h256_hex(str(task["model_hash_hex"]), "model_hash_hex"),
                _h256_hex(str(task["payload_hash_hex"]), "payload_hash_hex"),
                _h256_hex(str(task["commit_hash_hex"]), "commit_hash_hex"),
            )
        ),
        digest_size=H256_BYTES,
    ).digest()


def evaluate_fixture(path: Path = DEFAULT_VECTOR) -> dict[str, str | int]:
    """Validate canonical fields and demonstrate rejected legacy comparators."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    direct = payload["direct_rail_v1"]
    task = direct["task_hash"]["inputs"]
    report = direct["inputs"]

    canonical_task_preimage = task_preimage_v1(task)
    canonical_task_hash = task_hash_v1(task)
    if _h256_hex(str(report["task_hash_hex"]), "inputs.task_hash_hex") != canonical_task_hash:
        raise AssertionError("report_data fixture is not bound to its canonical task hash")
    canonical_report_preimage = report_preimage_v1(report)
    canonical_report_data = report_data_v1(report)
    expected_task_hash = _h256_hex(direct["task_hash"]["hash_hex"], "task_hash.hash_hex")
    expected_report_data = bytes.fromhex(direct["report_data_hex"])

    if canonical_task_preimage.hex() != direct["task_hash"]["preimage_hex"]:
        raise AssertionError("canonical task preimage does not match fixture")
    if canonical_task_hash != expected_task_hash:
        raise AssertionError("canonical task hash does not match fixture")
    if canonical_report_preimage.hex() != direct["report_data_preimage_hex"]:
        raise AssertionError("canonical report preimage does not match fixture")
    if canonical_report_data != expected_report_data:
        raise AssertionError("canonical report_data does not match fixture")
    if len(canonical_task_preimage) != 183:
        raise AssertionError("canonical task preimage must be 183 bytes")
    if len(canonical_report_preimage) != 145:
        raise AssertionError("canonical report preimage must be 145 bytes")
    if len(canonical_report_data) != REPORT_DATA_BYTES:
        raise AssertionError("canonical report_data must be 64 bytes")
    if canonical_report_data[H256_BYTES:] != b"\0" * H256_BYTES:
        raise AssertionError("canonical report_data must have a zero 32-byte suffix")

    legacy_u64 = legacy_task_hash(task, nonce_bytes=8)
    legacy_u32 = legacy_task_hash(task, nonce_bytes=4)
    bare_report_digest = hashlib.sha256(canonical_report_preimage).digest()
    if legacy_u64 == canonical_task_hash or legacy_u32 == canonical_task_hash:
        raise AssertionError("legacy §1.1 task form was accepted")
    if bare_report_digest == canonical_report_data or len(bare_report_digest) != 32:
        raise AssertionError("bare report digest was accepted as report_data")
    if not matches_canonical_v1(
        task,
        report,
        canonical_task_hash.hex(),
        canonical_report_data.hex(),
    ):
        raise AssertionError("canonical F.1 candidate was not accepted")
    if matches_canonical_v1(
        task,
        report,
        legacy_u64.hex(),
        canonical_report_data.hex(),
    ) or matches_canonical_v1(
        task,
        report,
        legacy_u32.hex(),
        canonical_report_data.hex(),
    ) or matches_canonical_v1(
        task,
        report,
        canonical_task_hash.hex(),
        bare_report_digest.hex(),
    ):
        raise AssertionError("legacy candidate was accepted")

    return {
        "fixture": str(path),
        "task_preimage_bytes": len(canonical_task_preimage),
        "task_hash_hex": canonical_task_hash.hex(),
        "report_preimage_bytes": len(canonical_report_preimage),
        "report_data_bytes": len(canonical_report_data),
        "report_data_hex": canonical_report_data.hex(),
        "legacy_u64_task_hash_hex": legacy_u64.hex(),
        "legacy_u32_task_hash_hex": legacy_u32.hex(),
        "bare_report_data_bytes": len(bare_report_digest),
        "result": "PASS: reference verifier accepts F.1 and rejects §1.1-shaped alternatives",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("vector", nargs="?", type=Path, default=DEFAULT_VECTOR)
    args = parser.parse_args()
    result = evaluate_fixture(args.vector)
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()