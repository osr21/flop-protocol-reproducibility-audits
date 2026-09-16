import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from task_id_conformance import (
    DEFAULT_VECTOR,
    evaluate_fixture,
    legacy_task_hash,
    matches_canonical_v1,
    report_data_v1,
    task_hash_v1,
)


class TaskIdConformanceTests(unittest.TestCase):
    def test_published_fixture_is_canonical_and_legacy_forms_are_rejected(self):
        result = evaluate_fixture()
        self.assertEqual(result["task_preimage_bytes"], 183)
        self.assertEqual(result["report_preimage_bytes"], 145)
        self.assertEqual(result["report_data_bytes"], 64)
        self.assertEqual(
            result["result"],
            "PASS: reference verifier accepts F.1 and rejects §1.1-shaped alternatives",
        )
        self.assertNotEqual(
            result["task_hash_hex"], result["legacy_u64_task_hash_hex"]
        )
        self.assertNotEqual(
            result["task_hash_hex"], result["legacy_u32_task_hash_hex"]
        )

    def test_wrong_field_width_is_rejected(self):
        import json

        direct = json.loads(DEFAULT_VECTOR.read_text())["direct_rail_v1"]
        task = dict(direct["task_hash"]["inputs"])
        task["agent_account_id32_hex"] = "11" * 31
        with self.assertRaises(ValueError):
            task_hash_v1(task)

    def test_bare_digest_is_not_report_data(self):
        import json
        import hashlib

        direct = json.loads(DEFAULT_VECTOR.read_text())["direct_rail_v1"]
        task = direct["task_hash"]["inputs"]
        report = direct["inputs"]
        canonical_task = task_hash_v1(task)
        canonical_report = report_data_v1(report)
        self.assertTrue(
            matches_canonical_v1(
                task, report, canonical_task.hex(), canonical_report.hex()
            )
        )
        self.assertFalse(
            matches_canonical_v1(
                task,
                report,
                legacy_task_hash(task, nonce_bytes=8).hex(),
                canonical_report.hex(),
            )
        )
        self.assertFalse(
            matches_canonical_v1(
                task,
                report,
                legacy_task_hash(task, nonce_bytes=4).hex(),
                canonical_report.hex(),
            )
        )
        self.assertFalse(
            matches_canonical_v1(
                task,
                report,
                canonical_task.hex(),
                hashlib.sha256(
                    bytes.fromhex(direct["report_data_preimage_hex"])
                ).hexdigest(),
            )
        )


if __name__ == "__main__":
    unittest.main()