import json
import subprocess
from pathlib import Path

import pytest

from weaponassambly.comparison import compare_certificates

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture
def certificate():
    return json.loads((REPO / 'tests/fixtures/tokyo_certification_golden.json').read_text())[
        'expected'
    ]


def test_match_ignores_key_order(certificate):
    assert compare_certificates(certificate, dict(reversed(list(certificate.items())))) == (
        True, 'MATCH\n'
    )


@pytest.mark.parametrize('field,value', [
    ('resolver_version', 2), ('certification_version', 2), ('digest_sha256', '0' * 64),
    ('platform', 'other'), ('display_name', 'other'), ('root', 'other'), ('module_count', 4),
])
def test_each_changed_claim_mismatches(certificate, field, value):
    changed = {**certificate, field: value}
    matched, report = compare_certificates(certificate, changed)
    assert not matched
    assert report.startswith('MISMATCH\n\n')
    assert f'{field}:\n  expected:' in report
    assert compare_certificates(certificate, changed)[1] == report


@pytest.mark.parametrize('bad', [None, [], {}, {'extra': 1}])
def test_invalid_certificate(certificate, bad):
    with pytest.raises(ValueError):
        compare_certificates(certificate, bad)


@pytest.mark.parametrize('field,value', [
    ('resolver_version', True), ('certification_version', 0), ('module_count', -1),
    ('module_count', 3.0), ('digest_sha256', 'xyz'), ('root', None),
])
def test_invalid_field(certificate, field, value):
    with pytest.raises(ValueError):
        compare_certificates(certificate, {**certificate, field: value})


def test_real_cli_certify_compare(tmp_path):
    import sys

    def run(*args):
        return subprocess.run(
            [sys.executable, '-m', 'weaponassambly.cli', *map(str, args)],
            capture_output=True, text=True, cwd=REPO,
        )

    first, second = tmp_path / 'first.json', tmp_path / 'second.json'
    build = REPO / 'configs/bm-s7.example.json'
    scene = REPO / 'examples/bm-s7.scene.json'
    for target in (first, second):
        assert run('certify', build, scene, '-o', target).returncode == 0
    result = run('compare', first, second)
    assert (result.returncode, result.stdout, result.stderr) == (0, 'MATCH\n', '')

    changed = json.loads(build.read_text())
    changed['display_name'] = 'Changed build'
    modified = tmp_path / 'modified.json'
    modified.write_text(json.dumps(changed))
    assert run('certify', modified, scene, '-o', second).returncode == 0
    result = run('compare', first, second)
    assert result.returncode == 1
    assert 'digest_sha256:\n  expected:' in result.stdout
    assert 'resolver_version: 1 == 1' in result.stdout
    assert not result.stderr

    second.write_text('{invalid')
    result = run('compare', first, second)
    assert result.returncode == 2
    assert result.stderr.startswith('ERROR:')
    assert not result.stdout
    result = run('compare', first, tmp_path / 'missing.json')
    assert result.returncode == 2
