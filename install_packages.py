"""Install a general AI coding toolkit into this project's dedicated environment."""
import argparse
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import venv

ROOT = Path(__file__).resolve().parent


def run(args, capture=False):
    print('>', subprocess.list2cmdline([str(x) for x in args]), flush=True)
    return subprocess.run([str(x) for x in args], check=True, text=True,
                          encoding='utf-8', capture_output=capture,
                          env={**os.environ, 'PYTHONUTF8': '1', 'PIP_DISABLE_PIP_VERSION_CHECK': '1'})


def atomic_text(path, text):
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         prefix=path.name + '.', suffix='.tmp', delete=False) as out:
            temp = Path(out.name)
            out.write(text)
        os.replace(temp, path)
    finally:
        if temp and temp.exists():
            temp.unlink()


def packages(profile):
    config = json.loads((ROOT / 'packages.json').read_text(encoding='utf-8'))
    return config['base'] | (config['extra'] if profile == 'all' else {})


def setup(profile='base', refresh=False, skip_browser=False, check_only=False):
    if sys.version_info < (3, 12) or struct.calcsize('P') != 8:
        raise RuntimeError('Use Python 3.12 or newer, 64-bit.')
    target = ROOT / '.venv'
    marker = target / 'server-starter.json'
    python = target / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    fingerprint = {'python': list(sys.version_info[:2]), 'owner': 'Python-Server-Starter'}
    if target.exists():
        if not marker.exists() or json.loads(marker.read_text()) != fingerprint:
            raise RuntimeError('Existing .venv belongs to another setup or Python minor version. '
                               'Keep it intact; use a new project folder or select the previous Python version.')
        if not python.exists():
            raise RuntimeError('Incomplete environment. Move .venv aside and retry.')
    elif check_only:
        raise RuntimeError('No environment installed yet.')
    else:
        venv.EnvBuilder(with_pip=True).create(target)
        atomic_text(marker, json.dumps(fingerprint))

    selected = packages(profile)
    lock = ROOT / f'requirements-{profile}-py{sys.version_info.major}{sys.version_info.minor}.lock.txt'
    if not check_only:
        run([python, '-m', 'pip', 'install', '--timeout', '60', '--retries', '2', '--upgrade', 'pip'])
        if lock.exists() and not refresh:
            install = ['-r', lock]
        else:
            install = [*(['--upgrade'] if refresh else []), *selected]
        # Wheels avoid unexpected compiler/toolchain installation on a fresh server.
        run([python, '-m', 'pip', 'install', '--timeout', '60', '--retries', '2',
             '--only-binary=:all:', *install])
    run([python, '-m', 'pip', 'check'])
    run([python, '-c', 'import importlib; modules=' + repr(list(selected.values())) +
         '; [importlib.import_module(m) for m in modules]; print("Imports OK:",len(modules))'])
    if not skip_browser:
        if not check_only:
            run([python, '-m', 'playwright', 'install', 'chromium'])
        run([python, '-c', 'from playwright.sync_api import sync_playwright\n'
             'with sync_playwright() as p:\n'
             ' b=p.chromium.launch(headless=True)\n'
             ' page=b.new_page(); page.set_content("<title>starter-ok</title>")\n'
             ' assert page.title()=="starter-ok"\n'
             ' b.close()\nprint("Chromium OK")'])
    if not check_only:
        freeze = run([python, '-m', 'pip', 'freeze'], capture=True).stdout
        atomic_text(lock, freeze)
    print('SUCCESS:', python)
    if skip_browser:
        print('Chromium installation/check skipped by request.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=['base', 'all'], default='base')
    parser.add_argument('--refresh', action='store_true')
    parser.add_argument('--skip-browser', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        setup(args.profile, args.refresh, args.skip_browser, args.check)
    except (subprocess.CalledProcessError, OSError, ValueError, RuntimeError) as exc:
        print('SETUP FAILED:', exc, file=sys.stderr)
        print('The environment may be partially installed. Fix the error and rerun. '
              'No successful lock snapshot was written by this failed run.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
