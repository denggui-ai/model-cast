"""Identity provenance checks use synthetic files, never generation."""
import hashlib
import json
import shutil

import pytest

from test_scripts import invoke, png, tmp_path  # noqa: F401 (worktree-local fixture)


@pytest.fixture
def handoff(tmp_path):
    face = png(tmp_path / 'approved/01.png', 2, 2)
    body = png(tmp_path / 'approved/04.png', 2, 3)
    garment = png(tmp_path / 'garment.png', 3, 3)
    lock = dict(schema=1, memory_points_zh=['synthetic point one', 'synthetic point two'])
    for role, source in [('face01', face), ('body04', body)]:
        lock[role] = dict(path=str(source), sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    lock_path = tmp_path / 'identity-lock.json'
    lock_path.write_text(json.dumps(lock))
    copied_face = tmp_path / 'attachment-02.png'
    copied_body = tmp_path / 'attachment-03.png'
    shutil.copyfile(face, copied_face)
    shutil.copyfile(body, copied_body)
    request = tmp_path / 'request.json'
    request.write_text(json.dumps(dict(prompt='synthetic, do not execute',
                                      referenced_image_paths=list(map(str, [garment, copied_face, copied_body])),
                                      transparent_background=False)))
    return lock_path, request, face, body, copied_face, copied_body


def check(handoff, face_index=2, body_index=3):
    result = invoke('check_identity_refs.py', '--identity-lock', handoff[0],
                    '--request', handoff[1], '--face-index', face_index, '--body-index', body_index)
    assert result.stdout, result.stderr
    assert json.loads(result.stdout)['status'] in {'ok', 'mismatch', 'invalid_input'}
    return result


def test_copied_approved_anchors_pass_without_writing_files(handoff, tmp_path):
    before = {p: p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    result = check(handoff)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['status'] == 'ok'
    assert before == {p: p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}


def test_another_person_is_rejected_even_with_self_consistent_metadata(handoff):
    _, request, _, _, face_copy, body_copy = handoff
    png(face_copy, 4, 4)
    png(body_copy, 4, 6)
    data = json.loads(request.read_text())
    data['refs'] = [dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                    for p in (face_copy, body_copy)]
    request.write_text(json.dumps(data))
    result = check(handoff)
    assert result.returncode == 1
    assert {p['role'] for p in json.loads(result.stdout)['problems']} == {'face01', 'body04'}


@pytest.mark.parametrize('changed', [2, 4])
def test_changed_approved_source_or_attachment_blocks_handoff(handoff, changed):
    handoff[changed].write_bytes(b'changed after approval or copying')
    assert check(handoff).returncode == 1


def test_swapped_identity_slots_are_rejected(handoff):
    assert check(handoff, face_index=3, body_index=2).returncode == 1


@pytest.mark.parametrize('mode', ['missing-body', 'missing-file', 'relative', 'wrong-shape', 'implicit'])
def test_incomplete_or_implicit_request_cannot_pass(handoff, mode):
    request = handoff[1]
    data = json.loads(request.read_text())
    if mode == 'missing-body':
        data['referenced_image_paths'].pop()
    elif mode == 'missing-file':
        handoff[5].unlink()
    elif mode == 'relative':
        data['referenced_image_paths'][1] = 'attachment-02.png'
    elif mode == 'wrong-shape':
        data['referenced_image_paths'] = 'not a list'
    else:
        data['num_last_images_to_include'] = 1
    request.write_text(json.dumps(data))
    assert check(handoff).returncode == 2


@pytest.mark.parametrize('face_index,body_index', [(0, 3), (2, 2), (2, 9)])
def test_invalid_identity_slots_cannot_pass(handoff, face_index, body_index):
    assert check(handoff, face_index, body_index).returncode == 2


def test_wrong_lock_schema_cannot_pass(handoff):
    lock = json.loads(handoff[0].read_text())
    lock['schema'] = 2
    handoff[0].write_text(json.dumps(lock))
    assert check(handoff).returncode == 2
