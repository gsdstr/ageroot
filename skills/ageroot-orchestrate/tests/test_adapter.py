"""Exercise role routing in the adapter without calling Orca."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ADAPTER = Path(__file__).resolve().parents[1] / 'orca/adapter.py'


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / '.agents').mkdir()
        binaries = self.root / 'bin'
        binaries.mkdir()
        for name in ('codex', 'claude'):
            binary = binaries / name
            binary.write_text('#!/bin/sh\nexit 0\n')
            binary.chmod(0o755)
        self.env = dict(os.environ, PATH=str(binaries), XDG_CONFIG_HOME=str(self.root / 'xdg'))
        (self.root / '.agents/roles.yaml').write_text('''version: 1
roles:
  coordinator:
    targets:
      - harness: codex
        model: gpt-test
  researcher:
    targets:
      - harness: claude
        model: claude-research
  builder:
    targets:
      - harness: codex
        model: gpt-builder
  reviewer:
    targets:
      - harness: codex
        model: gpt-review
      - harness: claude
        model: claude-review
''')

    def run_adapter(self, *args, cwd=None):
        return subprocess.run([sys.executable, '-I', str(ADAPTER), '--plan-id', 'test', *args],
                              cwd=cwd or self.root, env=self.env, text=True, capture_output=True)

    def test_dynamic_models_and_reviewer_independence(self):
        result = self.run_adapter('--workspace', str(self.root))
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(result.stdout)
        self.assertEqual(plan['routing_status'], 'resolved')
        self.assertEqual(plan['tasks'][2]['assigned_model'], 'gpt-builder')
        reviewer = plan['tasks'][3]
        self.assertEqual(reviewer['assigned_model'], 'claude-review')
        self.assertEqual(reviewer['assigned_harness'], 'claude')
        self.assertEqual(reviewer['resolution']['candidate_index'], 1)
        self.assertEqual(plan['orca_calls'], [])

    def test_nested_workspace_auto_discovery(self):
        nested = self.root / 'nested'
        nested.mkdir()
        result = self.run_adapter(cwd=nested)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['routing_status'], 'resolved')

    def test_disabled_role_blocks_apply_before_orca_call(self):
        (self.root / '.agents/roles.local.yaml').write_text('version: 1\nroles:\n  builder:\n    targets: []\n')
        dry = self.run_adapter()
        self.assertEqual(dry.returncode, 0, dry.stderr)
        plan = json.loads(dry.stdout)
        self.assertEqual(plan['routing_status'], 'unavailable')
        self.assertEqual(plan['tasks'][3]['resolution']['reason'], 'builder-unavailable-for-independence')
        apply = self.run_adapter('--apply')
        self.assertEqual(apply.returncode, 2)
        self.assertIn('role routing unavailable', apply.stderr)

    def test_opaque_builder_family_cannot_establish_independence(self):
        path = self.root / '.agents/roles.yaml'
        path.write_text(path.read_text().replace('gpt-builder', 'default'))
        result = self.run_adapter()
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(result.stdout)
        self.assertEqual(plan['routing_status'], 'unavailable')
        self.assertEqual(plan['tasks'][3]['resolution']['reason'], 'builder-family-unverified')

    def test_execute_requires_owner_start(self):
        result = self.run_adapter('--execute')
        self.assertEqual(result.returncode, 2)
        self.assertIn('Owner Start approval', result.stderr)


if __name__ == '__main__':
    unittest.main()
