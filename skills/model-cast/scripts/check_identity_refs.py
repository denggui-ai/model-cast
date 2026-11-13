"""Read-only provenance check of two identity slots in a native image request.

The lock must come from independently approved C4 originals. This checks file
bytes, not Owner approval, image quality, delivery to the tool, or future output.
"""
import argparse
import json
from pathlib import Path
import re

from gen_request import sha256


def absolute_file(value):
    if not isinstance(value, str) or not Path(value).is_absolute():
        raise ValueError('reference paths must be absolute')
    path = Path(value)
    if not path.is_file():
        raise ValueError('reference file missing: ' + value)
    return path


def check(lock, request, face_index, body_index):
    if not isinstance(lock, dict) or type(lock.get('schema')) is not int or lock['schema'] != 1:
        raise ValueError('identity-lock schema must be 1')
    if not isinstance(request, dict):
        raise ValueError('request must be a JSON object')
    refs = request.get('referenced_image_paths')
    if not isinstance(refs, list) or not refs:
        raise ValueError('native request requires referenced_image_paths')
    if request.get('num_last_images_to_include') is not None:
        raise ValueError('implicit recent-image references cannot be checked')
    if face_index == body_index or any(i < 1 or i > len(refs) for i in (face_index, body_index)):
        raise ValueError('identity indices must be distinct, in-range, and 1-based')
    paths = [absolute_file(value) for value in refs]
    checked, problems = [], []
    for role, index in [('face01', face_index), ('body04', body_index)]:
        entry = lock.get(role)
        if not isinstance(entry, dict) or not isinstance(entry.get('sha256'), str) or not re.fullmatch(r'[0-9a-f]{64}', entry['sha256']):
            raise ValueError(role + ': identity-lock sha256 invalid')
        source = absolute_file(entry.get('path'))
        expected = entry['sha256']
        actual = sha256(paths[index - 1])
        if sha256(source) != expected:
            problems.append(dict(role=role, reason='approved source hash changed'))
        if actual != expected:
            problems.append(dict(role=role, reason='request attachment does not match approved source'))
        checked.append(dict(role=role, index=index, path=str(paths[index - 1]), sha256=actual))
    return dict(status='mismatch' if problems else 'ok', checked=checked, problems=problems)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--identity-lock', required=True)
    parser.add_argument('--request', required=True)
    parser.add_argument('--face-index', type=int, required=True, help='1-based face01 slot in referenced_image_paths')
    parser.add_argument('--body-index', type=int, required=True, help='1-based body04 slot in referenced_image_paths')
    args = parser.parse_args()
    try:
        lock = json.loads(Path(args.identity_lock).read_text(encoding='utf-8'))
        request = json.loads(Path(args.request).read_text(encoding='utf-8'))
        result = check(lock, request, args.face_index, args.body_index)
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps(dict(status='invalid_input', error=str(exc)), ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result['problems'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
