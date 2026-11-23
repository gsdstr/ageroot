#!/usr/bin/env python3
"""Standalone, offline role routing. Requires only Python 3's standard library."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

ROLES = ('coordinator', 'researcher', 'author', 'builder', 'reviewer', 'integrator')
HARNESSES = ('agy', 'codex', 'claude', 'orca', 'hermes')
# Defaults are preferences, not claims of subscription/model availability.
DEFAULT_MODELS = {
    'agy': 'gemini-3.8-flash',
    'codex': 'gpt-5.6-sol',
    'claude': 'claude-sonnet-4-6',
    'orca': 'default',
    'hermes': 'default',
}
DEFAULTS = {
    role: {'targets': [
        {'harness': harness, 'model': DEFAULT_MODELS[harness]}
        for harness in (('codex', 'claude', 'agy', 'orca', 'hermes')
                        if role in ('author', 'reviewer', 'integrator')
                        else HARNESSES)
    ]}
    for role in ROLES
}


class ConfigError(ValueError):
    """Invalid role configuration, with source and line information."""


def parse_config(text: str, source: str = '<string>') -> dict:
    """Parse strict block YAML: two-space mappings and lists of target mappings.

    Deliberately excludes implicit YAML typing, anchors, tags, block scalars,
    flow collections (except []), and arbitrary YAML syntax.
    """
    lines = []

    def fail(number, message):
        raise ConfigError(f'{source}:line {number}: {message}')

    # Strip comments only outside quoted scalars. Preserve quoted # and colons.
    for number, raw in enumerate(text.splitlines(), 1):
        quote = None
        escaped = False
        end = len(raw)
        for index, char in enumerate(raw):
            if char == '\t':
                fail(number, 'tabs are unsupported')
            if escaped:
                escaped = False
                continue
            if quote == '"' and char == '\\':
                escaped = True
            elif quote and char == quote:
                quote = None
            elif not quote and char in ('"', "'"):
                quote = char
            elif not quote and char == '#' and (index == 0 or raw[index - 1].isspace()):
                end = index
                break
        body = raw[:end].rstrip()
        if not body:
            continue
        indent = len(body) - len(body.lstrip(' '))
        if indent % 2:
            fail(number, 'indentation must use multiples of two spaces')
        lines.append((indent, body[indent:], number))
    if not lines:
        fail(1, 'expected version and roles mapping')

    def scalar(value, number):
        if value == '[]':
            return []
        if value.startswith('"'):
            try:
                result = json.loads(value)
            except (ValueError, TypeError):
                fail(number, 'invalid double-quoted scalar')
            if not isinstance(result, str):
                fail(number, 'expected string scalar')
            return result
        if value.startswith("'"):
            if not re.fullmatch(r"'(?:[^']|'')*'", value):
                fail(number, 'invalid single-quoted scalar')
            return value[1:-1].replace("''", "'")
        if value.lower() in ('null', '~', 'true', 'false', '.nan', '.inf', '+.inf', '-.inf'):
            fail(number, 'null, boolean, and non-finite numeric scalars are unsupported')
        if re.fullmatch(r'[0-9]+', value):
            return int(value)
        if re.fullmatch(r'[-+]?(?:[0-9][0-9_]*(?:\.[0-9_]*)?(?:[eE][-+]?[0-9]+)?|\.[0-9]+(?:[eE][-+]?[0-9]+)?|0[xob][0-9a-fA-F_]+)', value):
            fail(number, 'numeric identifiers must be quoted')
        if not value or any(c in value for c in '{}[]&*!|>\'"') or ': ' in value or value.startswith(('-', '?', '@', '`')):
            fail(number, 'unsupported scalar or flow structure')
        return value

    def pair(body, number):
        match = re.fullmatch(r'([A-Za-z_][A-Za-z0-9_-]*):(?: +(.*))?', body)
        if not match:
            fail(number, 'expected block mapping key: value')
        return match.group(1), match.group(2)

    def mapping(index, indent, initial=None):
        result = {}
        locations = {}

        def put(key, raw_value, number, next_index, key_indent):
            if key in result:
                fail(number, f'duplicate key: {key}')
            locations[key] = number
            if raw_value is not None:
                result[key] = scalar(raw_value, number)
            else:
                if next_index >= len(lines) or lines[next_index][0] != key_indent + 2:
                    fail(number, f'{key} requires a value')
                result[key], next_index = block(next_index, key_indent + 2)
            return next_index

        if initial is not None:
            key, raw_value, number = initial
            index = put(key, raw_value, number, index, indent)
        while index < len(lines) and lines[index][0] == indent:
            _, body, number = lines[index]
            key, raw_value = pair(body, number)
            index = put(key, raw_value, number, index + 1, indent)
        if index < len(lines) and lines[index][0] > indent:
            fail(lines[index][2], 'unexpected indentation')
        # Retain locations separately for schema diagnostics without polluting data.
        positions[id(result)] = locations
        return result, index

    def block(index, indent):
        if not lines[index][1].startswith('- '):
            return mapping(index, indent)
        result = []
        while index < len(lines) and lines[index][0] == indent:
            _, body, number = lines[index]
            if not body.startswith('- '):
                fail(number, 'expected target list item')
            key, value = pair(body[2:], number)
            item, index = mapping(index + 1, indent + 2, (key, value, number))
            result.append(item)
        return result, index

    positions = {}
    if lines[0][0] != 0:
        fail(lines[0][2], 'top-level mapping must be unindented')
    data, index = mapping(0, 0)
    if index != len(lines):
        fail(lines[index][2], 'unexpected content')

    def shape(value, fields, label, number):
        if not isinstance(value, dict) or set(value) != set(fields):
            fail(number, f'{label} must contain exactly {", ".join(fields)}')

    shape(data, ('version', 'roles'), 'configuration', 1)
    if type(data['version']) is not int or data['version'] != 1:
        fail(positions[id(data)]['version'], 'version must be integer 1')
    if not isinstance(data['roles'], dict):
        fail(positions[id(data)]['roles'], 'roles must be a block mapping')
    for role, definition in data['roles'].items():
        number = positions[id(data['roles'])][role]
        if role not in ROLES:
            fail(number, f'unknown role: {role}')
        shape(definition, ('targets',), f'role {role}', number)
        targets = definition['targets']
        if not isinstance(targets, list):
            fail(number, f'{role}.targets must be a list')
        for target in targets:
            if not isinstance(target, dict) or not ({'harness', 'model'}.issubset(target) and set(target).issubset({'harness', 'model', 'effort'})):
                fail(number, 'candidate must contain harness, model, and optional effort')
            for key in ('harness', 'model'):
                value = target[key]
                if not isinstance(value, str) or not value.strip() or value != value.strip() or any(ord(c) < 32 for c in value):
                    fail(positions[id(target)][key], f'{key} must be a nonempty string')
            if 'effort' in target:
                value = target['effort']
                if not isinstance(value, str) or not value.strip() or value != value.strip() or any(ord(c) < 32 for c in value):
                    fail(positions[id(target)]['effort'], 'effort must be a nonempty string')
            if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', target['harness']):
                fail(positions[id(target)]['harness'], 'harness must be a PATH binary name')
    return data


def discover_workspace(explicit=None) -> Path:
    if explicit is not None:
        root = Path(explicit).expanduser().resolve()
        if not root.is_dir():
            raise ConfigError(f'workspace is not a directory: {root}')
        return root
    cwd = Path.cwd().resolve()
    for root in (cwd, *cwd.parents):
        if (root / '.agents').is_dir():
            return root
    raise ConfigError('no .agents/ workspace found; pass --workspace or --root')


def global_config_path() -> Path:
    return Path(os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config') / 'ageroot' / 'roles.yaml'


def load_roles(workspace: Path) -> dict:
    """Load every file strictly, then pick each role's entire winning definition."""
    layers = []
    for layer, path in (('local', workspace / '.agents/roles.local.yaml'),
                        ('team', workspace / '.agents/roles.yaml'),
                        ('global', global_config_path())):
        if path.exists():
            layers.append((layer, path, parse_config(path.read_text(encoding='utf-8'), str(path))['roles']))
    layers.append(('builtin', None, DEFAULTS))
    active = {}
    for role in ROLES:
        for layer, path, definitions in layers:
            if role in definitions:
                active[role] = {'layer': layer, 'path': str(path) if path else None,
                                'targets': [dict(t) for t in definitions[role]['targets']]}
                break
    return active


def model_family(model: str) -> str:
    name = model.lower().split('/')[-1]
    for prefix, family in (('gpt-', 'gpt'), ('codex', 'gpt'), ('o1', 'gpt'), ('o3', 'gpt'),
                           ('o4', 'gpt'), ('gemini', 'gemini'), ('claude', 'claude'),
                           ('llama', 'llama'), ('qwen', 'qwen'), ('deepseek', 'deepseek')):
        if name.startswith(prefix):
            return family
    # An opaque/default model cannot establish Reviewer family independence.
    return 'unknown'


def readiness(target: dict) -> str:
    if shutil.which(target['harness']) is None:
        return 'missing'
    # Binary presence verifies a known invocation surface only. Model access is
    # deliberately unverified offline (no provider/auth/network probe).
    return 'supported' if target['harness'] in ('agy', 'codex', 'claude') else 'unverified'


def resolve(role: str, active: dict, exclude_models=(), exclude_families=()) -> dict:
    config = active[role]
    result = {'version': 1, 'role': role, 'status': 'unavailable', 'layer': config['layer'],
              'target': None, 'candidate_index': None, 'rejections': []}
    for index, target in enumerate(config['targets']):
        state = readiness(target)
        family = model_family(target['model'])
        reason = None
        if target['model'] in exclude_models:
            reason = 'excluded-model'
        elif exclude_families and (family == 'unknown' or family in exclude_families):
            reason = 'excluded-family' if family != 'unknown' else 'unverified-family'
        elif state == 'missing':
            reason = 'missing-binary'
        if reason:
            result['rejections'].append({'candidate_index': index, 'target': target,
                                         'readiness': state, 'reason': reason})
            continue
        result.update(status='resolved', target=target, candidate_index=index,
                      readiness=state, family=family)
        return result
    result['reason'] = 'disabled' if not config['targets'] else 'targets-exhausted'
    return result


def dump_config(roles: dict) -> str:
    lines = ['version: 1', 'roles:']
    for role, definition in roles.items():
        lines.append(f'  {role}:')
        targets = definition['targets']
        if not targets:
            lines.append('    targets: []')
        else:
            lines.append('    targets:')
            for target in targets:
                lines.extend([f'      - harness: {json.dumps(target["harness"])}',
                              f'        model: {json.dumps(target["model"])}'])
                if 'effort' in target and target['effort'] is not None:
                    lines.append(f'        effort: {json.dumps(target["effort"])}')
    return '\n'.join(lines) + '\n'


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         prefix=f'.{path.name}.', delete=False) as stream:
            temporary = stream.name
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def setup(workspace: Path, scope: str, non_interactive: bool) -> dict:
    path = {'local': workspace / '.agents/roles.local.yaml',
            'team': workspace / '.agents/roles.yaml', 'global': global_config_path()}[scope]
    available = [harness for harness in HARNESSES if shutil.which(harness)]
    existing = parse_config(path.read_text(encoding='utf-8'), str(path))['roles'] if path.exists() else {}
    roles = {role: existing.get(role, {'targets': [dict(t) for t in DEFAULTS[role]['targets']
                                                  if t['harness'] in available]}) for role in ROLES}
    if not non_interactive:
        print(f'Detected harnesses: {", ".join(available) or "none"}; destination: {path}', file=sys.stderr)
        if input('Write configuration (preserving configured roles)? [y/N] ').strip().lower() not in ('y', 'yes'):
            return {'version': 1, 'status': 'cancelled', 'path': str(path)}
    content = dump_config(roles)
    parse_config(content, str(path))
    atomic_write(path, content)
    return {'version': 1, 'status': 'written', 'path': str(path), 'harnesses': available}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('--workspace', '--root', dest='workspace', default=argparse.SUPPRESS)
    # Accept workspace flags both before and after the subcommand.
    parser.add_argument('--workspace', '--root', dest='workspace')
    commands = parser.add_subparsers(dest='command', required=True)
    show = commands.add_parser('show', parents=[common])
    show.add_argument('--format', choices=('text', 'json'), default='text')
    show.add_argument('--json', action='store_true', help='alias for --format json')
    route = commands.add_parser('resolve', parents=[common])
    route.add_argument('role', choices=ROLES)
    route.add_argument('--exclude-model', action='append', default=[])
    route.add_argument('--exclude-family', action='append', default=[])
    configure = commands.add_parser('setup', parents=[common])
    scope = configure.add_mutually_exclusive_group()
    for name in ('local', 'team', 'global'):
        scope.add_argument('--' + name, dest='scope', action='store_const', const=name)
    configure.set_defaults(scope='local')
    configure.add_argument('--non-interactive', action='store_true')
    args = parser.parse_args(argv)
    try:
        # Machine-wide setup also works before a workspace exists.
        workspace = (Path.cwd() if args.command == 'setup' and args.scope == 'global'
                     and args.workspace is None else discover_workspace(args.workspace))
        if args.command == 'setup':
            print(json.dumps(setup(workspace, args.scope, args.non_interactive), indent=2))
        else:
            active = load_roles(workspace)
            if args.command == 'resolve':
                print(json.dumps(resolve(args.role, active, args.exclude_model, args.exclude_family), indent=2))
            elif args.format == 'json' or args.json:
                print(json.dumps({'version': 1, 'roles': active}, indent=2))
            else:
                print(f'{"ROLE":<14} {"LAYER":<8} TARGETS (in priority order)')
                for role, config in active.items():
                    targets = ', '.join(
                        f'{t["harness"]}/{t["model"]}' + (f' (effort: {t["effort"]})' if t.get('effort') else '') + f' [{readiness(t)}]'
                        for t in config['targets']
                    )
                    print(f'{role:<14} {config["layer"]:<8} {targets or "disabled"}')
        return 0
    except (ConfigError, OSError, EOFError) as error:
        print(json.dumps({'version': 1, 'status': 'error', 'error': str(error)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
