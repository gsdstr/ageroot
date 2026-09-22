import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate.py"
SPEC = importlib.util.spec_from_file_location("orchestration_validate", SCRIPT)
validate = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(validate)


class ValidationTests(unittest.TestCase):
    def test_manifest_is_valid(self):
        validate.validate_manifest(validate.load_json_yaml(validate.ROOT / "manifest.yaml"))

    def test_scaffold_paths_exist(self):
        self.assertTrue((validate.ROOT / "phases").is_dir())
        self.assertTrue((validate.ROOT / "lifecycle-map.md").is_file())

    def test_complete_package_is_valid(self):
        validate.validate_package()

    def test_unknown_role_is_rejected(self):
        with self.assertRaisesRegex(validate.ValidationError, "unknown participating role"):
            validate.validate_phase({
                "metadata": {"id": "x", "phase_index": 1, "name": "x", "summary": "x"},
                "participating_roles": ["NotARole"], "entry_criteria": {}, "exit_criteria": {},
                "handoff_artifacts": [], "budget_slice": {"iterations": 0, "agent_turns": 0, "model_capability_units": 0, "wall_clock_minutes": 0}, "escalation_gates": [],
            })

    def test_missing_phase_field_is_rejected(self):
        with self.assertRaisesRegex(validate.ValidationError, "phase missing"):
            validate.validate_phase({"participating_roles": []})

    def test_incompatible_handoff_is_rejected(self):
        with self.assertRaisesRegex(validate.ValidationError, "producer_role"):
            validate.validate_handoff(
                {"id": "x", "from_phase": "intake", "to_phase": "research-planning", "producer_role": "Builder", "consumer_role": "Author", "artifact_schema": "x"},
                {"Owner", "Coordinator"}, {"Researcher", "Author"},
            )

    def test_excessive_budget_is_rejected(self):
        phase = validate.load_frontmatter(validate.ROOT / "phases" / "01-intake.md")
        phase["budget_slice"]["agent_turns"] = 31
        with self.assertRaisesRegex(validate.ValidationError, "budget slices exceed"):
            validate.validate_budget({"intake": phase})

    def test_absent_owner_gate_is_rejected(self):
        lifecycle = validate.load_frontmatter(validate.ROOT / "lifecycle-map.md")
        lifecycle["owner_gates"] = lifecycle["owner_gates"][1:]
        with self.assertRaisesRegex(validate.ValidationError, "missing a required Owner gate"):
            validate.validate_lifecycle(lifecycle)

    def test_self_review_policy_is_enforced(self):
        phase = validate.load_frontmatter(validate.ROOT / "phases" / "03-implementation.md")
        phase["exit_criteria"]["reviewer_independence"] = False
        with self.assertRaisesRegex(validate.ValidationError, "reviewer independence"):
            validate.validate_reviewer_independence(phase)
