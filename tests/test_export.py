import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def run(*args):
    return subprocess.run(
        [sys.executable, '-m', 'weaponassambly.cli', *map(str, args)],
        cwd=REPO, capture_output=True, text=True,
    )


@pytest.fixture
def inputs(tmp_path):
    build = REPO / 'configs/bm-s7.example.json'
    scene = REPO / 'examples/bm-s7.scene.json'
    cert = tmp_path / 'reference.json'
    assert run('certify', build, scene, '-o', cert).returncode == 0
    return build, scene, cert


def test_export_is_repeatable_and_embeds_matching_certificate(inputs, tmp_path):
    build, scene, cert = inputs
    output = tmp_path / 'nested/export.json'
    command = ('export', build, scene, '--expected', cert, '-o', output)
    first = run(*command)
    assert first.returncode == 0, first.stderr
    assert first.stdout.startswith('MATCH\nWROTE:')
    content = output.read_bytes()
    assert run(*command).returncode == 0
    assert output.read_bytes() == content
    data = json.loads(content)
    assert data['certification'] == json.loads(cert.read_text())
    resolved = run('resolve', build, scene)
    assert resolved.returncode == 0
    assert data['payload'] == json.loads(resolved.stdout)
    assert data['export_version'] == 1


@pytest.mark.parametrize('existing', [True, False])
def test_changed_build_blocks_export(inputs, tmp_path, existing):
    build, scene, cert = inputs
    changed = json.loads(build.read_text())
    changed['display_name'] = 'Changed'
    modified = tmp_path / 'build.json'
    modified.write_text(json.dumps(changed))
    output = tmp_path / 'export.json'
    if existing:
        output.write_text('preserve me')
    result = run('export', modified, scene, '--expected', cert, '-o', output)
    assert result.returncode == 1
    assert result.stdout.startswith('MISMATCH\n')
    assert 'digest_sha256:' in result.stdout
    assert not result.stderr
    assert output.read_text() == 'preserve me' if existing else not output.exists()


def test_invalid_reference_and_output_error(inputs, tmp_path):
    build, scene, cert = inputs
    output = tmp_path / 'export.json'
    cert.write_text('{}')
    result = run('export', build, scene, '--expected', cert, '-o', output)
    assert result.returncode == 2
    assert result.stderr.startswith('ERROR:')
    assert not output.exists()
    assert run('certify', build, scene, '-o', cert).returncode == 0
    result = run('export', build, scene, '--expected', cert, '-o', tmp_path)
    assert result.returncode == 2
    assert result.stderr.startswith('ERROR:')
    assert 'MATCH' not in result.stdout
