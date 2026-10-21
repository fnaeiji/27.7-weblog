#!/usr/bin/env python3
"""Check for potential secrets in codebase."""

import os
import re

patterns = [
    (r'(password|secret|api_key|token)\s*=\s*[\'"]([^\'"]{8,})', 'potential secret'),
]

excluded_paths = {'.git', '.venv', '__pycache__', '.pytest_cache', 'node_modules', '.env.example'}

found = False
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in excluded_paths and not d.startswith('.')]
    for f in files:
        if f in excluded_paths:
            continue
        if not any(
            f.endswith(ext)
            for ext in (
                '.py',
                '.md',
                '.txt',
                '.yml',
                '.yaml',
                '.json',
                '.toml',
                '.ini',
                '.cfg',
                '.env',
            )
        ):
            continue
        p = os.path.join(root, f)
        try:
            with open(p, encoding='utf-8') as fp:
                content = fp.read()
            for pattern, desc in patterns:
                for m in re.finditer(pattern, content, re.I):
                    val = m.group(2)
                    if 'change-me' in val or 'dev-secret' in val or 'example' in p:
                        continue
                    if len(val) >= 8:
                        print(f'{p}: {desc} = {val[:20]}...')
                        found = True
        except Exception:
            pass

if not found:
    print('No potential secrets found in codebase.')
