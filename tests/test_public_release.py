"""Regression tests for path, structured-content and Git release safeguards."""
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import check_public_release as release_check
import generate_sha256_manifest as manifest_generator


class ReleaseTests(unittest.TestCase):
    def test_reviewed_global_aggregate_metadata_allowed(self):
        self.assertIsNone(release_check.is_blocked_path(
            "RELAX_Global_SHAP/Numerical_Reproduction/RELAX_global_SHAP_run_metadata.json"
        ))

    def test_participant_outputs_blocked(self):
        self.assertIsNotNone(release_check.is_blocked_path(
            "RELAX_Participant_Level/outputs/result.csv"
        ))

    def test_local_workspace_blocked(self):
        self.assertIsNotNone(release_check.is_blocked_path(
            "SSAQS_Global_SHAP_Analysis/notebook.ipynb"
        ))

    def test_public_aggregate_not_blocked(self):
        self.assertIsNone(release_check.is_blocked_path(
            "RELAX_Global_SHAP/RELAX_global_SHAP_summary.csv"
        ))

    def test_csv_sensitive_header_detected(self):
        result = release_check.inspect_structured_content(
            "export.csv",
            b"participant_id,timestamp,score\\nP01,2024-01-01,0.4\\n",
        )
        self.assertIn("participant_id", result)
        self.assertIn("timestamp", result)

    def test_aggregate_header_allowed(self):
        self.assertIsNone(release_check.inspect_structured_content(
            "summary.csv", b"feature,mean_shap,rank\\nx,0.4,1\\n"
        ))

    def test_camel_case_sensitive_headers_detected(self):
        result = release_check.inspect_structured_content(
            "export.csv", b"participantId,rowIndex,score\\nP01,12,0.4\\n"
        )
        self.assertIn("participantId", result)
        self.assertIn("rowIndex", result)

    def test_jsonl_sensitive_field_in_later_record_detected(self):
        payload = (
            b'{"safeField":1}\n'
            b'{"participantId":"P02","score":0.7}\n'
        )
        result = release_check.inspect_structured_content("records.jsonl", payload)
        self.assertIn("participantId", result)

    def test_malformed_jsonl_record_fails_closed(self):
        payload = (
            b'{"safeField":1}\n'
            b'{"participantId":\n'
        )
        result = release_check.inspect_structured_content("records.jsonl", payload)
        self.assertIn("invalid JSONL record at line 2", result)

    def test_large_json_is_inspected_without_truncation(self):
        payload = (
            '{"padding":"' + ("x" * 2_100_000) + '","participantId":"P01"}'
        ).encode("utf-8")
        result = release_check.inspect_structured_content("large.json", payload)
        self.assertIn("participantId", result)

    def test_json_sensitive_field_after_first_100_list_items_detected(self):
        records = [{"safeField": i} for i in range(100)]
        records.append({"participantId": "P01"})
        payload = json.dumps(records).encode("utf-8")
        result = release_check.inspect_structured_content("export.json", payload)
        self.assertIn("participantId", result)

    @unittest.skipUnless(shutil.which("git"), "Git unavailable")
    def test_staged_sensitive_content_detected_even_with_generic_filename(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            f = root / "export.csv"
            f.write_text("participant_id,timestamp,score\\nP01,2024-01-01,0.4\\n")
            subprocess.run(["git", "-C", str(root), "add", "export.csv"], check=True)
            f.unlink()
            found, note = release_check.staged_findings(root)
            self.assertIsNone(note)
            self.assertTrue(any("participant_id" in x for x in found))

    @unittest.skipUnless(shutil.which("git"), "Git unavailable")
    def test_historical_sensitive_content_detected_under_generic_filename(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email",
                            "test@example.org"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name",
                            "Test"], check=True)
            f = root / "archive_export.csv"
            f.write_text("participant_id,timestamp,score\\nP01,2024-01-01,0.4\\n")
            subprocess.run(["git", "-C", str(root), "add", f.name], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm",
                            "add generic export"], check=True)
            f.unlink()
            subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm",
                            "remove export"], check=True)
            found, note = release_check.history_findings(root)
            self.assertIsNone(note)
            self.assertTrue(any(
                "historical archive_export.csv" in x and "participant_id" in x
                for x in found
            ))

    @unittest.skipUnless(shutil.which("git"), "Git unavailable")
    def test_historical_restricted_path_detected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email",
                            "test@example.org"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name",
                            "Test"], check=True)
            f = root / "RELAX_next_morning_stress_dataset.csv"
            f.write_text("participant_id,timestamp,target\\nP01,2024-01-01,1\\n")
            subprocess.run(["git", "-C", str(root), "add", f.name], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "test"],
                           check=True)
            f.unlink()
            subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "remove"],
                           check=True)
            found, note = release_check.history_findings(root)
            self.assertIsNone(note)
            self.assertTrue(any("historical" in x for x in found))

    @unittest.skipUnless(shutil.which("git"), "Git unavailable")
    def test_manifest_uses_index_blob_not_unstaged_working_tree(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email",
                            "test@example.org"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name",
                            "Test"], check=True)

            tracked = root / "aggregate.csv"
            tracked.write_bytes(b"feature,mean_shap\\nfeature_a,0.25\\n")
            subprocess.run(["git", "-C", str(root), "add", "aggregate.csv"],
                           check=True)

            # Deliberately change the working tree without staging the change.
            tracked.write_bytes(b"participant_id,timestamp\\nP01,2024-01-01\\n")

            entries = manifest_generator.generate_manifest(root)
            expected = hashlib.sha256(
                b"feature,mean_shap\\nfeature_a,0.25\\n"
            ).hexdigest()
            self.assertIn(f"{expected}  aggregate.csv", entries)
            self.assertNotIn(
                hashlib.sha256(tracked.read_bytes()).hexdigest(),
                [line.split()[0] for line in entries],
            )

            manifest_text = (root / "SHA256SUMS.txt").read_text(encoding="utf-8")
            self.assertIn(f"{expected}  aggregate.csv", manifest_text)


if __name__ == "__main__":
    unittest.main()
