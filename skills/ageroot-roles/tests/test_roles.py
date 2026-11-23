"""Offline contracts for the standalone role router."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/roles.py'
SPEC = importlib.util.spec_from_file_location('roles', SCRIPT)
roles = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(roles)


def config(role='builder', targets=None):
    return roles.dump_config({role: {'targets': targets if targets is not None else [
        {'harness': 'codex', 'model': 'gpt-test'}]}})


class ParserTests(unittest.TestCase):
    def test_block_yaml_and_comments(self):
        parsed = roles.parse_config('# comment\n' + config() + '# end\n')
        self.assertEqual(parsed['roles']['builder']['targets'][0]['model'], 'gpt-test')

    def test_disable(self):
        self.assertEqual(roles.parse_config(config(targets=[]))['roles']['builder']['targets'], [])

    def test_single_quotes_and_comment(self):
        text = "version: 1\nroles:\n  builder:\n    targets:\n      - harness: 'codex' # hi\n        model: 'my''model#id'\n"
        self.assertEqual(roles.parse_config(text)['roles']['builder']['targets'][0]['model'], "my'model#id")

    def test_candidate_order_preserved(self):
        targets = [{'harness': 'codex', 'model': 'one'}, {'harness': 'agy', 'model': 'two'}]
        self.assertEqual(roles.parse_config(config(targets=targets))['roles']['builder']['targets'], targets)

    def test_target_with_effort(self):
        text = "version: 1\nroles:\n  builder:\n    targets:\n      - harness: codex\n        model: gpt-test\n        effort: high\n"
        parsed = roles.parse_config(text)
        self.assertEqual(parsed['roles']['builder']['targets'][0]['effort'], 'high')

    def test_dump_config_preserves_effort(self):
        dumped = roles.dump_config({'builder': {'targets': [{'harness': 'codex', 'model': 'gpt-test', 'effort': 'high'}]}})
        self.assertIn('effort: "high"', dumped)
        parsed = roles.parse_config(dumped)
        self.assertEqual(parsed['roles']['builder']['targets'][0]['effort'], 'high')

    def test_invalid_configs(self):
        valid = config()
        cases = {
            'wrong version': valid.replace('version: 1', 'version: 2'),
            'quoted version': valid.replace('version: 1', 'version: "1"'),
            'duplicate version': 'version: 1\n' + valid,
            'duplicate roles': valid + 'roles:\n  author:\n    targets: []\n',
            'duplicate role': valid + '  builder:\n    targets: []\n',
            'duplicate targets': valid + '    targets: []\n',
            'duplicate candidate key': valid + '        model: other\n',
            'missing model': valid.replace('        model: "gpt-test"\n', ''),
            'missing harness': valid.replace('      - harness: "codex"\n        model:', '      - model:'),
            'extra field': valid + '        extra: nope\n',
            'extra root': valid + 'extra: nope\n',
            'unknown role': valid.replace('builder:', 'janitor:'),
            'missing targets': 'version: 1\nroles:\n  builder:\n    other: []\n',
            'null target': valid.replace('targets:\n      - harness: "codex"\n        model: "gpt-test"', 'targets: null'),
            'null model': valid.replace('"gpt-test"', 'null'),
            'empty model': valid.replace('"gpt-test"', '""'),
            'numeric model': valid.replace('"gpt-test"', '123'),
            'float model': valid.replace('"gpt-test"', '1.5'),
            'exponent model': valid.replace('"gpt-test"', '1e3'),
            'empty effort': valid + '        effort: ""\n',
            'null effort': valid + '        effort: null\n',
            'numeric effort': valid + '        effort: 123\n',
            'uppercase boolean': valid.replace('"gpt-test"', 'TRUE'),
            'hex model': valid.replace('"gpt-test"', '0x12'),
            'numeric harness': valid.replace('"codex"', '123'),
            'absolute harness': valid.replace('"codex"', '"/bin/codex"'),
            'flow mapping': 'version: 1\nroles: {builder: {targets: []}}',
            'flow sequence': valid.replace('targets:\n      - harness: "codex"\n        model: "gpt-test"', 'targets: [codex]'),
            'list scalar': valid.replace('- harness: "codex"\n        model: "gpt-test"', '- codex'),
            'missing role value': 'version: 1\nroles:\n  builder:\n',
            'missing roles': 'version: 1',
            'empty': '',
            'bad indentation': valid.replace('  builder:', '   builder:'),
            'indent skip': valid.replace('  builder:', '    builder:'),
            'tabs': valid.replace('  builder:', '\tbuilder:'),
            'anchor': valid.replace('"gpt-test"', '&model'),
            'tag': valid.replace('"gpt-test"', '!!str model'),
            'block scalar': valid.replace('"gpt-test"', '|'),
            'unclosed quote': valid.replace('"gpt-test"', '"oops'),
        }
        for label, text in cases.items():
            with self.subTest(label=label), self.assertRaisesRegex(roles.ConfigError, r'line \d+'):
                roles.parse_config(text)


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.workspace = self.root / 'workspace'
        (self.workspace / '.agents').mkdir(parents=True)
        self.global_path = self.root / 'xdg/ageroot/roles.yaml'
        self.env = patch.dict(os.environ, {'XDG_CONFIG_HOME': str(self.root / 'xdg')})
        self.env.start()
        self.addCleanup(self.env.stop)

    def write(self, layer, text):
        path = {'global': self.global_path, 'team': self.workspace / '.agents/roles.yaml',
                'local': self.workspace / '.agents/roles.local.yaml'}[layer]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def cli(self, *args, cwd=None, env=None):
        return subprocess.run([sys.executable, '-I', str(SCRIPT), *args], cwd=cwd or self.workspace,
                              env=env, text=True, capture_output=True)

    def test_four_layers_and_granular_inheritance(self):
        self.write('global', config('researcher'))
        self.write('team', config('author'))
        self.write('local', config('builder'))
        active = roles.load_roles(self.workspace)
        self.assertEqual({r: active[r]['layer'] for r in ('researcher', 'author', 'builder', 'reviewer')},
                         {'researcher': 'global', 'author': 'team', 'builder': 'local', 'reviewer': 'builtin'})

    def test_same_role_precedence_and_list_replacement(self):
        self.write('global', config(targets=[{'harness': 'agy', 'model': 'global'}]))
        self.write('team', config(targets=[{'harness': 'codex', 'model': 'team'}]))
        self.write('local', config(targets=[{'harness': 'claude', 'model': 'local'}]))
        active = roles.load_roles(self.workspace)
        self.assertEqual(active['builder']['targets'], [{'harness': 'claude', 'model': 'local'}])
        self.assertEqual(active['builder']['layer'], 'local')
        (self.workspace / '.agents/roles.local.yaml').unlink()
        self.assertEqual(roles.load_roles(self.workspace)['builder']['layer'], 'team')
        (self.workspace / '.agents/roles.yaml').unlink()
        self.assertEqual(roles.load_roles(self.workspace)['builder']['layer'], 'global')
        self.global_path.unlink()
        self.assertEqual(roles.load_roles(self.workspace)['builder']['layer'], 'builtin')

    def test_strict_exhaustion(self):
        self.write('local', config(targets=[{'harness': 'absent', 'model': 'local'}]))
        self.write('team', config())
        with patch.object(roles.shutil, 'which', side_effect=lambda h: '/bin/codex' if h == 'codex' else None):
            result = roles.resolve('builder', roles.load_roles(self.workspace))
        self.assertEqual(result['status'], 'unavailable')
        self.assertEqual(result['layer'], 'local')
        self.assertEqual(result['rejections'][0]['reason'], 'missing-binary')

    def test_disable_overrides_available_lower_layer(self):
        self.write('team', config())
        self.write('local', config(targets=[]))
        with patch.object(roles.shutil, 'which', return_value='/bin/codex'):
            result = roles.resolve('builder', roles.load_roles(self.workspace))
        self.assertEqual(result['reason'], 'disabled')
        self.assertIsNone(result['target'])

    def test_shadowed_invalid_config_fails_fast(self):
        self.write('local', config())
        self.write('global', 'version: 9\nroles:\n  builder:\n    targets: []\n')
        with self.assertRaises(roles.ConfigError):
            roles.load_roles(self.workspace)

    def test_ordered_pre_dispatch_traversal_and_readiness(self):
        self.write('local', config(targets=[{'harness': 'absent', 'model': 'one'},
                                          {'harness': 'codex', 'model': 'gpt-two'}]))
        with patch.object(roles.shutil, 'which', side_effect=lambda h: '/bin/codex' if h == 'codex' else None):
            result = roles.resolve('builder', roles.load_roles(self.workspace))
            self.assertEqual(roles.readiness({'harness': 'absent'}), 'missing')
        self.assertEqual(result['candidate_index'], 1)
        self.assertEqual(result['readiness'], 'supported')
        with patch.object(roles.shutil, 'which', return_value='/bin/anything'):
            self.assertEqual(roles.readiness({'harness': 'hermes'}), 'unverified')

    def test_reviewer_exclusions_and_unknown_family(self):
        candidates = [{'harness': 'codex', 'model': 'gpt-a'}, {'harness': 'codex', 'model': 'codex-b'},
                      {'harness': 'orca', 'model': 'default'}, {'harness': 'agy', 'model': 'gemini-c'}]
        self.write('local', config('reviewer', candidates))
        with patch.object(roles.shutil, 'which', return_value='/bin/anything'):
            result = roles.resolve('reviewer', roles.load_roles(self.workspace), ['gpt-a'], ['gpt'])
        self.assertEqual(result['candidate_index'], 3)
        self.assertEqual([r['reason'] for r in result['rejections']],
                         ['excluded-model', 'excluded-family', 'unverified-family'])

    def test_family_classification(self):
        self.assertEqual(roles.model_family('provider/claude-sonnet-x'), 'claude')
        self.assertEqual(roles.model_family('codex-auto-review'), 'gpt')
        self.assertEqual(roles.model_family('default'), 'unknown')

    def test_upward_discovery(self):
        nested = self.workspace / 'a/b'
        nested.mkdir(parents=True)
        with patch.object(Path, 'cwd', return_value=nested):
            self.assertEqual(roles.discover_workspace(), self.workspace)
        with patch.object(Path, 'cwd', return_value=self.root):
            with self.assertRaisesRegex(roles.ConfigError, 'no .agents/'):
                roles.discover_workspace()

    def test_explicit_workspace(self):
        self.assertEqual(roles.discover_workspace(self.root), self.root)
        with self.assertRaises(roles.ConfigError):
            roles.discover_workspace(self.root / 'missing')

    def test_global_home_fallback(self):
        with patch.dict(os.environ, {'XDG_CONFIG_HOME': ''}), patch.object(Path, 'home', return_value=self.root):
            self.assertEqual(roles.global_config_path(), self.root / '.config/ageroot/roles.yaml')

    def test_cli_workspace_root_before_and_after_subcommand(self):
        for args in [('--workspace', str(self.workspace), 'show', '--format', 'json'),
                     ('show', '--root', str(self.workspace), '--json'),
                     ('--root', str(self.workspace), 'show', '--json')]:
            result = self.cli(*args, cwd=self.root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['roles']['builder']['layer'], 'builtin')

    def test_show_text(self):
        result = self.cli('show')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('TARGETS', result.stdout)
        self.assertIn('reviewer', result.stdout)

    def test_resolve_target_with_effort(self):
        self.write('local', config('reviewer', [{'harness': 'codex', 'model': 'gpt-test', 'effort': 'high'}]))
        result = self.cli('resolve', 'reviewer')
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['status'], 'resolved')
        self.assertEqual(data['target']['effort'], 'high')

    def test_cli_exclusion_flags(self):
        self.write('local', config('reviewer', [{'harness': 'codex', 'model': 'gpt-test'}]))
        env = dict(os.environ, PATH='')
        result = self.cli('resolve', 'reviewer', '--exclude-model', 'gpt-test', '--exclude-family', 'gpt', env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['rejections'][0]['reason'], 'excluded-model')

    def test_cli_invalid_config_json_error(self):
        self.write('local', 'version: 2\nroles:\n  builder:\n    targets: []\n')
        result = self.cli('resolve', 'builder')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)['status'], 'error')
        self.assertFalse(result.stdout)

    def test_setup_all_destinations(self):
        for scope in ('local', 'team', 'global'):
            result = self.cli('setup', '--' + scope, '--non-interactive', env=dict(os.environ, PATH=''))
            self.assertEqual(result.returncode, 0, result.stderr)
            receipt = json.loads(result.stdout)
            parsed = roles.parse_config(Path(receipt['path']).read_text())
            self.assertEqual(set(parsed['roles']), set(roles.ROLES))
            self.assertTrue(all(not r['targets'] for r in parsed['roles'].values()))

    def test_setup_probes_path_and_preserves_configured_roles(self):
        self.write('local', config('builder', []))
        with patch.object(roles.shutil, 'which', side_effect=lambda h: '/bin/' + h if h in ('codex', 'agy') else None):
            receipt = roles.setup(self.workspace, 'local', True)
        parsed = roles.parse_config(Path(receipt['path']).read_text())
        self.assertEqual(parsed['roles']['builder']['targets'], [])
        self.assertEqual([t['harness'] for t in parsed['roles']['researcher']['targets']], ['agy', 'codex'])
        self.assertEqual(list(Path(receipt['path']).parent.glob('.roles.local.yaml.*')), [])

    def test_setup_global_outside_workspace(self):
        result = self.cli('setup', '--global', '--non-interactive', cwd=self.root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.global_path.exists())

    def test_interactive_setup_cancellation(self):
        with patch('builtins.input', return_value='n'), patch('sys.stderr'):
            result = roles.setup(self.workspace, 'local', False)
        self.assertEqual(result['status'], 'cancelled')
        self.assertFalse((self.workspace / '.agents/roles.local.yaml').exists())

    def test_atomic_failure_preserves_original(self):
        path = self.write('local', config())
        before = path.read_text()
        with patch.object(roles.os, 'replace', side_effect=OSError('failure')):
            with self.assertRaises(OSError):
                roles.atomic_write(path, 'changed')
        self.assertEqual(path.read_text(), before)
        self.assertEqual(list(path.parent.glob('.roles.local.yaml.*')), [])


if __name__ == '__main__':
    unittest.main()
