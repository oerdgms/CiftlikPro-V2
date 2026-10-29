"""Regenerate/check distribution identities from app/release_info.py.

Run before packaging; --check is read-only and fails on release drift.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'app'))
import release_info as release


def expected_files():
    sw = ROOT/'app/mobile_assets/service-worker.js'
    installer = ROOT/'installer.iss'
    workflow = ROOT/'.github/workflows/windows-installer.yml'
    return {
        sw: re.sub(r"const CACHE = '[^']+';", f"const CACHE = '{release.CACHE_NAME}';", sw.read_text(encoding='utf-8'), count=1),
        installer: re.sub(r'^OutputBaseFilename=.*$', 'OutputBaseFilename='+release.SETUP_STEM, installer.read_text(encoding='utf-8'), flags=re.M),
        workflow: re.sub(r'CiftlikPro-Enterprise-V3\.9\.23-DEV4-AppEdition-[\w.-]+-Windows-Setup', release.ARTIFACT_NAME,
                    re.sub(r'CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_[\w]+_Setup\.exe', release.SETUP_FILE, workflow.read_text(encoding='utf-8'))),
        ROOT/'RELEASE.json': json.dumps(release.metadata(), ensure_ascii=False, indent=2)+'\n',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    drift = []
    for path, expected in expected_files().items():
        current = path.read_text(encoding='utf-8') if path.exists() else None
        if current != expected:
            drift.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.write_text(expected, encoding='utf-8', newline='\n')
    if args.check and drift:
        print('Sürüm dosyaları uyumsuz: '+', '.join(drift), file=sys.stderr)
        return 1
    print(release.BUILD+(' — kontrol başarılı' if args.check else ' — sürüm dosyaları eşitlendi'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
