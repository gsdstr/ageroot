"""Tests for Ageroot distribution module."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from ageroot_core.comparison import AgerootUpdateEngine, DeterministicNormalizer, DryRunOptions, ResultClass, SimpleYamlHelper, SnapshotStore, Strategy
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
        self.assertIn(".agents/skills/ageroot-orchestrate/manifest.yaml", renders)
        self.assertIn(".agents/skills/ageroot-orchestrate/orca/adapter.py", renders)
        self.assertIn(".agents/skills/ageroot-roles/scripts/roles.py", renders)
        self.assertIn(".agents/.gitignore", renders)
        self.assertNotIn("orchestration", get_default_components())
        self.assertNotIn("orca_adapter", get_default_components())
        self.assertFalse(any(p.startswith(".agents/orchestration/") for p in renders))
        # Memory is opt-in, so not present in default
        self.assertNotIn(".agents/skills/memory-manager/SKILL.md", renders)

        # All entries in managed_files must be concrete files, not ending in slash
        for entry in managed_files:
            self.assertFalse(entry["path"].endswith("/"))

    def test_opt_in_memory_component(self):
        renders, _ = collect_payload(self.repo_root, selected_components=["core", "ageroot-orchestrate", "ageroot-roles", "memory"])
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

    def legacy_consumer(self):
        """Seed a genuine baseline-backed old installation without old sources."""
        service = DistributionService(repo_root=self.repo_root)
        target = self.temp_dir / "legacy"
        service.export_payload(target, components=["core"])
        state_path = target / ".agents/ageroot.state.yaml"
        state = SimpleYamlHelper.parse(state_path.read_text())
        for relative in (".agents/orchestration/manifest.yaml",
                         ".agents/orchestration/orca/adapter.py",
                         ".agents/protocols/orchestration.md"):
            content = "legacy managed content\n"
            path = target / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            snapshot = ".agents/snapshots/" + relative
            snapshot_path = target / snapshot
            snapshot_path.parent.mkdir(parents=True, exist_ok=True)
            snapshot_path.write_text(content)
            state["managed_files"].append({"path": relative, "strategy": "generated",
                                          "snapshot": snapshot,
                                          "sha256": SnapshotStore.compute_sha256(content)})
        state_path.write_text(SimpleYamlHelper.dump(state))
        return service, target

    def test_legacy_state_migrates_through_standard_engine(self):
        service, target = self.legacy_consumer()
        local = target / ".agents/roles.local.yaml"
        local.write_text("user-owned role preferences\n")
        clean, drift = service.check_drift(target)
        self.assertFalse(clean)
        self.assertTrue(any("unexpected: .agents/orchestration/" in d for d in drift))
        report, outcome = service.sync_local(target, allow_deletions=True)
        self.assertTrue(outcome.success, outcome.error)
        state = SimpleYamlHelper.parse((target / ".agents/ageroot.state.yaml").read_text())
        paths = {entry["path"] for entry in state["managed_files"]}
        self.assertIn(".agents/skills/ageroot-roles/scripts/roles.py", paths)
        self.assertIn(".agents/skills/ageroot-orchestrate/orca/adapter.py", paths)
        self.assertIn(".agents/.gitignore", paths)
        self.assertIn("roles.local.yaml", (target / ".agents/.gitignore").read_text())
        self.assertFalse(any(p.startswith(".agents/orchestration/") for p in paths))
        self.assertNotIn(".agents/protocols/orchestration.md", paths)
        self.assertNotIn(".agents/roles.local.yaml", paths)
        self.assertEqual(local.read_text(), "user-owned role preferences\n")
        self.assertEqual(service.check_drift(target), (True, []))

    def test_legacy_deletions_still_require_confirmation(self):
        service, target = self.legacy_consumer()
        report, outcome = service.sync_local(target)
        self.assertFalse(outcome.success)
        self.assertTrue((target / ".agents/orchestration/manifest.yaml").exists())

    def test_modified_legacy_file_blocks_atomic_migration(self):
        service, target = self.legacy_consumer()
        legacy = target / ".agents/orchestration/manifest.yaml"
        legacy.write_text("locally modified legacy data\n")
        report, outcome = service.sync_local(target, allow_deletions=True)
        self.assertFalse(outcome.success)
        self.assertEqual(legacy.read_text(), "locally modified legacy data\n")
        self.assertFalse((target / ".agents/skills/ageroot-roles").exists())

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
