#!/usr/bin/env python3
"""Reproduce the §1.1 versus Appendix F.1 hash/wire divergence.

This intentionally uses only the Python standard library.  It consumes the
published vector instead of inventing fixture inputs.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VECTOR = ROOT / "evidence" / "wire-format-v1.json"


def h256(value: bytes) -> bytes:
    return hashlib.blake2b(value, digest_size=32).digest()


def hx(value: bytes) -> str:
    return value.hex()


def main() -> None:
    corpus = json.loads(VECTOR.read_text())
    direct = corpus["direct_rail_v1"]
    values = direct["task_hash"]["inputs"]
    genesis = bytes.fromhex(values["genesis_hash_hex"])
    agent = bytes.fromhex(values["agent_account_id32_hex"])
    model = bytes.fromhex(values["model_hash_hex"])
    payload = bytes.fromhex(values["payload_hash_hex"])
    commit = bytes.fromhex(values["commit_hash_hex"])
    nonce = int(values["nonce"])

    # §1.1, using the fixture's fixed-width integer convention where the
    # prose itself is silent.
    old_task_preimage = (
        agent
        + nonce.to_bytes(8, "little")
        + model
        + payload
        + commit
    )
    old_task_hash = h256(old_task_preimage)

    # Appendix F.1 and the executable generator.
    new_task_preimage = (
        b"FLOP/POUI/TASK"
        + b"\x01"
        + genesis
        + old_task_preimage
    )
    new_task_hash = h256(new_task_preimage)
    expected_task_hash = bytes.fromhex(direct["task_hash"]["hash_hex"])
    assert new_task_hash == expected_task_hash
    assert old_task_hash != new_task_hash

    current_report_preimage = bytes.fromhex(direct["report_data_preimage_hex"])
    old_report_preimage = old_task_hash + current_report_preimage[32:]
    old_report_digest = hashlib.sha256(old_report_preimage).digest()
    current_report_digest = hashlib.sha256(current_report_preimage).digest()
    current_report_data = bytes.fromhex(direct["report_data_hex"])
    assert current_report_digest == current_report_data[:32]
    assert len(current_report_data) == 64
    assert old_report_digest != current_report_digest

    print("§1.1 task:   %d bytes -> %s" % (len(old_task_preimage), hx(old_task_hash)))
    print("F.1 task:    %d bytes -> %s" % (len(new_task_preimage), hx(new_task_hash)))
    print(
        "§1.1 report: %d bytes -> %s"
        % (len(old_report_preimage), hx(old_report_digest))
    )
    print(
        "F.1 report:  %d bytes + 32-byte pad -> %s"
        % (len(current_report_preimage), hx(current_report_digest))
    )
    print("PASS: legacy and v1 task/report bindings diverge")


if __name__ == "__main__":
    main()