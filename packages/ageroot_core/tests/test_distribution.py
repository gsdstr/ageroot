"""Tests for Ageroot distribution module."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from ageroot_core.comparison import AgerootUpdateEngine, DryRunOptions, ResultClass, Strategy
from ageroot_core.distribution.collector import collect_payload
from ageroot_core.distribution.manifest import get_default_components
from ageroot_core.distribution.service import DistributionService


class DistributionModuleTests(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[3]
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ageroot_dist_test_"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_default_components_collection(self):
        renders, managed_files = collect_payload(self.repo_root)
        self.assertGreater(len(renders), 30)
        self.assertIn("AGENTS.md", renders)
        self.assertIn(".agents/AGENTS.md", renders)
        self.assertIn(".agents/orchestration/manifest.yaml", renders)
        self.assertIn(".agents/orchestration/orca/adapter.py", renders)
        # Memory is opt-in, so not present in default
        self.assertNotIn(".agents/skills/memory-manager/SKILL.md", renders)

        # All entries in managed_files must be concrete files, not ending in slash
        for entry in managed_files:
            self.assertFalse(entry["path"].endswith("/"))

    def test_opt_in_memory_component(self):
        renders, _ = collect_payload(self.repo_root, selected_components=["core", "orchestration", "orca_adapter", "memory"])
        self.assertIn(".agents/skills/memory-manager/SKILL.md", renders)
        self.assertIn(".agents/skills/memory-maintenance/SKILL.md", renders)

    def test_export_and_drift_check(self):
        service = DistributionService(repo_root=self.repo_root)
        export_dir = self.temp_dir / "export"
        service.export_payload(output_dir=export_dir)

        # Clean check must pass
        clean, drift = service.check_drift(target_dir=export_dir)
        self.assertTrue(clean)
        self.assertEqual(drift, [])

        # State file must exist with valid managed_files
        state_file = export_dir / ".agents" / "ageroot.state.yaml"
        self.assertTrue(state_file.exists())

        # Modify a file -> drift detected
        target_file = export_dir / ".agents" / "rules" / "rtk-rules.md"
        target_file.write_text("TAMPERED", encoding="utf-8")
        clean, drift = service.check_drift(target_dir=export_dir)
        self.assertFalse(clean)
        self.assertTrue(any("modified: .agents/rules/rtk-rules.md" in d for d in drift))

        # Add unexpected file in managed prefix -> drift detected
        unexpected = export_dir / ".agents" / "protocols" / "unexpected.txt"
        unexpected.write_text("UNEXPECTED", encoding="utf-8")
        clean, drift = service.check_drift(target_dir=export_dir)
        self.assertFalse(clean)
        self.assertTrue(any("unexpected: .agents/protocols/unexpected.txt" in d for d in drift))

    def test_update_engine_dry_run_with_renders(self):
        service = DistributionService(repo_root=self.repo_root)
        export_dir = self.temp_dir / "consumer"
        service.export_payload(output_dir=export_dir)

        # Run engine dry-run on consumer
        renders, _ = collect_payload(self.repo_root)
        engine = AgerootUpdateEngine(root_dir=export_dir)
        report = engine.dry_run(renders)

        # Since it was just exported, everything should be UNCHANGED (or eligible)
        self.assertTrue(report.is_eligible)
        conflicts = [r for r in report.results.values() if r.result_class == ResultClass.CONFLICT]
        blocked = [r for r in report.results.values() if r.result_class == ResultClass.BLOCKED]
        self.assertEqual(len(conflicts), 0)
        self.assertEqual(len(blocked), 0)


if __name__ == "__main__":
    unittest.main()
