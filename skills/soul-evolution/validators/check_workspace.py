#!/usr/bin/env python3
"""
Soul Evolution Workspace Boundary Check
MUST run before ANY Soul Evolution pipeline operation.

Verifies that the current workspace actually has Soul Evolution installed.
Prevents cross-agent contamination when multiple agents/workspaces exist.

Usage:
  python3 soul-evolution/validators/check_workspace.py [--workspace-root .]

Checks:
  1. soul-evolution/SKILL.md exists (Soul Evolution is installed here)
  2. soul-evolution/config.json exists and is valid JSON
  3. SOUL.md exists and contains Soul Evolution tags ([CORE]/[MUTABLE])
  4. SOUL.md contains the Evolution Protocol section
  5. memory/ directory exists

If ANY check fails → Soul Evolution is NOT installed in this workspace.
The pipeline MUST NOT run. This prevents editing the wrong agent's SOUL.

Exit code: 0 = safe to proceed, 1 = STOP (wrong workspace)
"""

import json
import os
import sys


def check(workspace_root='.'):
    errors = []
    warnings = []

    workspace_root = os.path.abspath(workspace_root)
    workspace_name = os.path.basename(workspace_root)

    # ========================================
    # 1. Soul Evolution installation marker
    # ========================================
    skill_path = os.path.join(workspace_root, 'soul-evolution', 'SKILL.md')
    if not os.path.exists(skill_path):
        errors.append({
            'check': 'soul_evolution_installed',
            'message': (
                f'soul-evolution/SKILL.md not found in workspace "{workspace_name}" ({workspace_root}). '
                f'Soul Evolution is NOT installed here. '
                f'STOP — do not run the Soul Evolution pipeline in this workspace. '
                f'You may be running under the wrong agent.'
            )
        })
        # Early return — no point checking anything else
        return {
            'status': 'FAIL',
            'workspace': workspace_root,
            'workspace_name': workspace_name,
            'soul_evolution_installed': False,
            'errors': errors,
            'warnings': warnings
        }

    # ========================================
    # 1b. Symlink target validation
    # ========================================
    soul_evo_dir = os.path.join(workspace_root, 'soul-evolution')
    if os.path.islink(soul_evo_dir):
        link_target = os.path.realpath(soul_evo_dir)
        if not os.path.isdir(link_target):
            warnings.append({
                'check': 'soul_evolution_symlink',
                'message': (
                    f'soul-evolution is a symlink but its target does not exist: {link_target}. '
                    f'Plugin config sync will write to a different location than the workspace.'
                )
            })

    # ========================================
    # 2. Config exists and is valid
    # ========================================
    config_path = os.path.join(workspace_root, 'soul-evolution', 'config.json')
    if not os.path.exists(config_path):
        errors.append({
            'check': 'config',
            'message': 'soul-evolution/config.json not found'
        })
    else:
        try:
            with open(config_path) as f:
                cfg = json.load(f)
            if not isinstance(cfg, dict):
                errors.append({
                    'check': 'config',
                    'message': 'soul-evolution/config.json is not a valid JSON object'
                })
        except json.JSONDecodeError as e:
            errors.append({
                'check': 'config',
                'message': f'soul-evolution/config.json is invalid JSON: {e}'
            })

    # ========================================
    # 3. SOUL.md exists and has Soul Evolution tags
    # ========================================
    soul_path = os.path.join(workspace_root, 'SOUL.md')
    if not os.path.exists(soul_path):
        errors.append({
            'check': 'soul_exists',
            'message': (
                f'SOUL.md not found in workspace "{workspace_name}". '
                f'Soul Evolution requires a SOUL.md file.'
            )
        })
    else:
        with open(soul_path, 'r') as f:
            soul_content = f.read()

        has_core = '[CORE]' in soul_content
        has_mutable = '[MUTABLE]' in soul_content

        if not has_core and not has_mutable:
            errors.append({
                'check': 'soul_tags',
                'message': (
                    f'SOUL.md in "{workspace_name}" has no [CORE] or [MUTABLE] tags. '
                    f'This SOUL.md has not been set up for Soul Evolution. '
                    f'STOP — you may be looking at the wrong agent\'s SOUL.md.'
                )
            })

        # ========================================
        # 4. Evolution Protocol present
        # ========================================
        has_evolution = 'evolution protocol' in soul_content.lower() or 'soul evolution' in soul_content.lower()
        if not has_evolution:
            warnings.append({
                'check': 'evolution_protocol',
                'message': (
                    'SOUL.md does not mention "Evolution protocol" or "Soul Evolution". '
                    'This may not be the right agent. Proceed with caution.'
                )
            })

    # ========================================
    # 5. Memory directory
    # ========================================
    memory_dir = os.path.join(workspace_root, 'memory')
    if not os.path.isdir(memory_dir):
        warnings.append({
            'check': 'memory_dir',
            'message': 'memory/ directory not found (may need to be created on first run)'
        })

    # ========================================
    # 6. Reality data schemas
    # ========================================
    reality_dir = os.path.join(workspace_root, 'memory', 'reality')
    if os.path.isdir(reality_dir):
        # interior.json
        interior_path = os.path.join(reality_dir, 'interior.json')
        if os.path.exists(interior_path):
            try:
                with open(interior_path) as f:
                    interior = json.load(f)
                if not isinstance(interior, dict) or 'rooms' not in interior:
                    warnings.append({
                        'check': 'interior_schema',
                        'message': 'interior.json must have a "rooms" array'
                    })
                elif not isinstance(interior['rooms'], list):
                    warnings.append({
                        'check': 'interior_schema',
                        'message': 'interior.json "rooms" must be an array'
                    })
            except json.JSONDecodeError as e:
                warnings.append({
                    'check': 'interior_json',
                    'message': f'interior.json is invalid JSON: {e}'
                })

        # inventory.json
        inventory_path = os.path.join(reality_dir, 'inventory.json')
        if os.path.exists(inventory_path):
            try:
                with open(inventory_path) as f:
                    inventory = json.load(f)
                if not isinstance(inventory, dict) or 'items' not in inventory:
                    warnings.append({
                        'check': 'inventory_schema',
                        'message': 'inventory.json must have an "items" array'
                    })
                elif not isinstance(inventory['items'], list):
                    warnings.append({
                        'check': 'inventory_schema',
                        'message': 'inventory.json "items" must be an array'
                    })
            except json.JSONDecodeError as e:
                warnings.append({
                    'check': 'inventory_json',
                    'message': f'inventory.json is invalid JSON: {e}'
                })

        # cycle.json (optional, but validated when present)
        cycle_path = os.path.join(reality_dir, 'cycle.json')
        if os.path.exists(cycle_path):
            try:
                with open(cycle_path) as f:
                    cycle_data = json.load(f)
                if not isinstance(cycle_data, dict):
                    warnings.append({
                        'check': 'cycle_schema',
                        'message': 'cycle.json must be a JSON object'
                    })
                else:
                    required_cycle = {'cycle_length', 'current_day', 'phase', 'hormones', 'symptom_modifiers', 'simulator'}
                    missing_fields = required_cycle - set(cycle_data.keys())
                    if missing_fields:
                        warnings.append({
                            'check': 'cycle_schema',
                            'message': f'cycle.json missing required fields: {sorted(missing_fields)}'
                        })
                    else:
                        if cycle_data.get('cycle_length') != 28:
                            warnings.append({
                                'check': 'cycle_length',
                                'message': f'cycle.json cycle_length must be 28, got: {cycle_data.get("cycle_length")}'
                            })
                        day = cycle_data.get('current_day', 0)
                        if not isinstance(day, int) or not (1 <= day <= 28):
                            warnings.append({
                                'check': 'cycle_day',
                                'message': f'cycle.json current_day must be integer 1-28, got: {day}'
                            })
                        valid_phases = {'menstruation', 'follicular', 'ovulation', 'luteal'}
                        if cycle_data.get('phase') not in valid_phases:
                            warnings.append({
                                'check': 'cycle_phase',
                                'message': f'cycle.json phase must be one of {sorted(valid_phases)}, got: {cycle_data.get("phase")}'
                            })
            except json.JSONDecodeError as e:
                warnings.append({
                    'check': 'cycle_json',
                    'message': f'cycle.json is invalid JSON: {e}'
                })

        # hobbies.json (optional, validated when present)
        hobbies_path = os.path.join(reality_dir, 'hobbies.json')
        if os.path.exists(hobbies_path):
            try:
                with open(hobbies_path) as f:
                    hobbies_data = json.load(f)
                if not isinstance(hobbies_data, dict) or 'hobbies' not in hobbies_data:
                    warnings.append({
                        'check': 'hobbies_schema',
                        'message': 'hobbies.json must have a "hobbies" array'
                    })
                elif not isinstance(hobbies_data['hobbies'], list):
                    warnings.append({
                        'check': 'hobbies_schema',
                        'message': 'hobbies.json "hobbies" must be an array'
                    })
                else:
                    for i, h in enumerate(hobbies_data['hobbies']):
                        if not isinstance(h, dict):
                            warnings.append({
                                'check': 'hobbies_entry',
                                'message': f'hobbies.json entry {i} must be an object'
                            })
                            continue
                        required_fields = {'id', 'name', 'category', 'added_at', 'total_sessions', 'total_minutes', 'log'}
                        missing = required_fields - set(h.keys())
                        if missing:
                            warnings.append({
                                'check': 'hobbies_entry',
                                'message': f'hobbies.json entry {i} ("{h.get("name", "?")}") missing fields: {sorted(missing)}'
                            })
            except json.JSONDecodeError as e:
                warnings.append({
                    'check': 'hobbies_json',
                    'message': f'hobbies.json is invalid JSON: {e}'
                })

        # dream_state.json (optional, validated when present)
        dream_state_path = os.path.join(reality_dir, 'dream_state.json')
        if os.path.exists(dream_state_path):
            try:
                with open(dream_state_path) as f:
                    dream_data = json.load(f)
                if not isinstance(dream_data, dict):
                    warnings.append({
                        'check': 'dream_state_schema',
                        'message': 'dream_state.json must be a JSON object'
                    })
                else:
                    required_dream = {'active', 'started_at', 'moments'}
                    missing_fields = required_dream - set(dream_data.keys())
                    if missing_fields:
                        warnings.append({
                            'check': 'dream_state_schema',
                            'message': f'dream_state.json missing required fields: {sorted(missing_fields)}'
                        })
                    if not isinstance(dream_data.get('active'), bool):
                        warnings.append({
                            'check': 'dream_state_active',
                            'message': f'dream_state.json "active" must be boolean, got: {type(dream_data.get("active")).__name__}'
                        })
                    if not isinstance(dream_data.get('moments'), list):
                        warnings.append({
                            'check': 'dream_state_moments',
                            'message': 'dream_state.json "moments" must be an array'
                        })
            except json.JSONDecodeError as e:
                warnings.append({
                    'check': 'dream_state_json',
                    'message': f'dream_state.json is invalid JSON: {e}'
                })

    # development/manifest.json
    dev_manifest_path = os.path.join(workspace_root, 'memory', 'development', 'manifest.json')
    if os.path.exists(dev_manifest_path):
        try:
            with open(dev_manifest_path) as f:
                manifest = json.load(f)
            if not isinstance(manifest, dict) or 'projects' not in manifest:
                warnings.append({
                    'check': 'dev_manifest_schema',
                    'message': 'development/manifest.json must have a "projects" array'
                })
            elif not isinstance(manifest['projects'], list):
                warnings.append({
                    'check': 'dev_manifest_schema',
                    'message': 'development/manifest.json "projects" must be an array'
                })
        except json.JSONDecodeError as e:
            warnings.append({
                'check': 'dev_manifest_json',
                'message': f'development/manifest.json is invalid JSON: {e}'
            })

    # ========================================
    # 7. Validators present
    # ========================================
    validators_dir = os.path.join(workspace_root, 'soul-evolution', 'validators')
    if not os.path.isdir(validators_dir):
        warnings.append({
            'check': 'validators',
            'message': 'soul-evolution/validators/ directory not found'
        })

    status = 'FAIL' if errors else 'PASS'
    return {
        'status': status,
        'workspace': workspace_root,
        'workspace_name': workspace_name,
        'soul_evolution_installed': len(errors) == 0 or (len(errors) > 0 and os.path.exists(skill_path)),
        'errors': errors,
        'warnings': warnings
    }


if __name__ == '__main__':
    workspace = '.'
    if '--workspace-root' in sys.argv:
        idx = sys.argv.index('--workspace-root')
        if idx + 1 < len(sys.argv):
            workspace = sys.argv[idx + 1]

    result = check(workspace)
    print(json.dumps(result, indent=2))

    if result['status'] == 'FAIL':
        print(
            f'\n🚨 WORKSPACE BOUNDARY VIOLATION: Soul Evolution pipeline must NOT run '
            f'in "{result["workspace_name"]}". Check your agent/cron configuration.',
            file=sys.stderr
        )

    sys.exit(0 if result['status'] == 'PASS' else 1)
