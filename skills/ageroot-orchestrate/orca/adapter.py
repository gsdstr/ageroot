#!/usr/bin/env python3
"""Dry-run mapper from neutral lifecycle to Orca supervised state."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys

PHASES = ["intake", "research-planning", "implementation", "review-integration"]

PHASE_ROLES = dict(zip(PHASES, ('coordinator', 'researcher', 'builder', 'reviewer')))
ROLES_SCRIPT = Path(__file__).resolve().parents[2] / 'ageroot-roles/scripts/roles.py'


def resolve_role(role, workspace, builder=None):
    command = [sys.executable, str(ROLES_SCRIPT), 'resolve', role]
    if workspace is not None:
        command.extend(['--workspace', str(workspace)])
    if role == 'reviewer' and builder and builder['status'] == 'resolved':
        command.extend(['--exclude-model', builder['target']['model'],
                        '--exclude-family', builder['family']])
    return json.loads(subprocess.check_output(command, text=True))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan-id", required=True)
    parser.add_argument("--mode", choices=["neutral", "orca"], default="orca")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--start-approved", action="store_true")
    parser.add_argument("--workspace", "--root", type=Path)
    args = parser.parse_args()
    if args.mode != "orca":
        parser.error("adapter requires --mode orca")
    if args.execute and not args.start_approved:
        parser.error("--execute requires recorded Owner Start approval")
    audit = f".planning/{args.plan_id}/orca"
    commands = [["orca", "orchestration", "run-create", "--objective", args.plan_id, "--json"]]
    wait_loop_command = [
        "orca",
        "orchestration",
        "check",
        "--wait",
        "--types",
        "worker_done,escalation,question",
        "--timeout-ms",
        "900000",
        "--json",
    ]
    tasks = []
    builder = None
    for index, phase in enumerate(PHASES):
        role = PHASE_ROLES[phase]
        try:
            resolution = resolve_role(role, args.workspace, builder)
        except (OSError, subprocess.CalledProcessError, ValueError) as error:
            parser.error(f'role resolution failed for {role}: {error}')
        if role == 'builder':
            builder = resolution
        if role == 'reviewer':
            reason = None
            if not builder or builder['status'] != 'resolved':
                reason = 'builder-unavailable-for-independence'
            elif builder['family'] == 'unknown':
                reason = 'builder-family-unverified'
            if reason:
                resolution.update(status='unavailable', target=None, candidate_index=None, reason=reason)
        target = resolution.get('target') or {}
        harness = target.get('harness')
        tasks.append({
            'phase': phase,
            'role': role.title(),
            'assigned_harness': harness,
            'assigned_agent': 'antigravity' if harness == 'agy' else harness,
            'assigned_model': target.get('model'),
            'assigned_effort': target.get('effort'),
            'resolution': resolution,
            'depends_on': PHASES[index - 1:index],
        })
    blocked = any(task['resolution']['status'] != 'resolved' for task in tasks)
    if blocked and (args.apply or args.execute):
        parser.error('role routing unavailable; inspect dry-run resolution traces before dispatch')
    plan = {
        "mode": "execute-plan" if args.execute else "apply" if args.apply else "dry-run",
        "run": {"owner_task": args.plan_id},
        "tasks": tasks,
        "routing_status": "unavailable" if blocked else "resolved",
        "decision_tasks": ["Start", "Plan-to-Build", "Final Acceptance"],
        "audit": {"run_map": f"{audit}/run-map.json", "decision_packets": f"{audit}/decision-packets/"},
        "coordinator_wait_loop": wait_loop_command,
        "orca_calls": [] if not args.apply else commands,
        "planned_orca_commands": commands,
    }
    if args.apply:
        receipt = json.loads(subprocess.check_output(commands[0], text=True))
        plan["apply_receipt"] = receipt
        plan["warning"] = "Run created; task DAG/Dispatch remains explicit adapter follow-up."
    if args.execute:
        plan["warning"] = (
            "Start approved; worktree/Dispatch commands require reviewed task specs and role-to-harness mapping. "
            "Coordinator must maintain active supervision loop."
        )
    print(json.dumps(plan, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
