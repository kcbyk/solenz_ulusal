#!/usr/bin/env python3
"""Rebuild the Sinepad single-file site before deploying/building the TV APK.
Run from anywhere: python scripts/sync_site.py
"""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parent.parent
subprocess.run(['python3', str(root / 'source/build_sinepad.py')], check=True)
source = (root / 'source/Sinepad-TV.html').read_bytes()
(root / 'site/index.html').write_bytes(source)
print(f'Synchronized site/index.html ({len(source):,} bytes). APK bundles this file too.')
