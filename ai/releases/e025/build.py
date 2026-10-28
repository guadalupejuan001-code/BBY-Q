#!/usr/bin/env python3
"""Reproduce and verify the delivered E025 capsule without retraining it."""
import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def build(runtime, output, assets=None):
    runtime = str(Path(runtime).resolve())
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    release = json.loads((ROOT / 'release.json').read_text())
    for name, key in [('BBY-Q.rxe', 'app'), ('code.rxe', 'code'), ('controller.rvp', 'seed')]:
        data = gzip.decompress(base64.b64decode((ROOT / (name + '.gz.b64')).read_text()))
        if digest(data) != release['sha256'][key]:
            raise ValueError('E025 capsule checksum mismatch: ' + name)
        (output / name).write_bytes(data)

    def run(*args):
        return subprocess.check_output([runtime, *map(str, args)], text=True)

    # The recovered textual XI is the disassembly of the delivered code. Compile
    # it again and compare normalized instructions, including every operand.
    run('compile', ROOT / 'conversation-linked.xi', output / 'recompiled.rxe', 'BBY Q interface XI')
    run('disassemble', output / 'recompiled.rxe', output / 'recompiled.xi')
    if (output / 'recompiled.xi').read_bytes() != (ROOT / 'conversation-linked.xi').read_bytes():
        raise ValueError('E025 source and compiled code disagree')
    run('pack-app', output / 'code.rxe', output / 'controller.rvp', output / 'repacked.rxe',
        release['id'], release['title'], release['version'], release['source'])
    if (output / 'repacked.rxe').read_bytes() != (output / 'BBY-Q.rxe').read_bytes():
        raise ValueError('E025 application could not be reproduced exactly')
    metadata = json.loads(run('inspect-rxe', output / 'BBY-Q.rxe'))

    android = output / 'android'
    android.mkdir(exist_ok=True)
    for source in (ROOT / 'android').rglob('*'):
        if not source.is_file():
            continue
        relative = source.relative_to(ROOT / 'android')
        data = source.read_bytes()
        if relative.name.endswith('.gz.b64'):
            relative = relative.with_name(relative.name[:-7])
            data = gzip.decompress(base64.b64decode(data))
        target = android / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    manifest = json.loads((android / 'manifest.json').read_text())
    curriculum_data = (android / 'upgrade-chain.json').read_bytes()
    if digest(curriculum_data) != manifest['chain']['curriculum_sha256']:
        raise ValueError('E025 curriculum checksum mismatch')
    curriculum = json.loads(curriculum_data)
    for module in curriculum['modules'].values():
        if digest((android / module['file']).read_bytes()) != module['sha256']:
            raise ValueError('E025 curriculum module checksum mismatch')
    if digest((android / 'W4u.rxe').read_bytes()) != manifest['agents']['artifact_sha256']:
        raise ValueError('W4u identity changed')
    shutil.copy2(android / 'W4u.rxe', output / 'W4u.rxe')
    # Required by the native host fixture as well as the Android installer.
    shutil.copy2(android / 'manifest.json', output / 'manifest.json')
    for name in ['upgrade-e016.rxe', 'upgrade-control.rxe', 'upgrade-w4u.rxe', 'upgrade-chain-ui.rxe']:
        shutil.copy2(android / name, output / name)
    if assets is not None:
        assets = Path(assets).resolve()
        shutil.copytree(android, assets / 'bbyq-interface', dirs_exist_ok=True)
        (assets / 'native-apps').mkdir(parents=True, exist_ok=True)
        shutil.copy2(output / 'BBY-Q.rxe', assets / 'native-apps' / 'BBY-Q.rxe')
    report = {'version': release['version'], 'metadata': metadata,
              'app_sha256': release['sha256']['app'],
              'w4u_sha256': manifest['agents']['artifact_sha256'],
              'exact_repack': True, 'source_recompiled_and_equivalent': True,
              'curriculum_modules_verified': len(curriculum['modules'])}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('runtime')
    parser.add_argument('output')
    parser.add_argument('--assets')
    args = parser.parse_args()
    print(json.dumps(build(args.runtime, args.output, args.assets), indent=2))
