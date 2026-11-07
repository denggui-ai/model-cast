"""Prepare an explicit-reference request; never execute generation."""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import shlex

CLI_VERSION = 'codex-cli 0.161.0'
HOST_PREFIX = '【宿主指令】不要调用任何技能、插件或脚本，不要读写文件；使用内置图片生成工具完成下面的请求，生成且只生成 1 张图。'


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def now():
    return datetime.now(timezone(timedelta(hours=8))).isoformat()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('task', 'purpose', 'id', 'prompt-file', 'run-dir'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--ref', action='append', default=[])
    parser.add_argument('--identity-lock')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+', args.id):
        parser.error('id must be a simple filename component')
    if not args.ref and args.purpose not in {'t0', 'diagram'}:
        parser.error('explicit references required')
    if args.purpose == 'diagram' and args.ref:
        parser.error('diagram must not have references')
    refs = []
    try:
        prompt = Path(args.prompt_file).expanduser().resolve(strict=True)
        prompt_hash = sha256(prompt)
        for value in args.ref:
            role, filename = value.split('=', 1)
            if role not in {'product', 'selection', 'face01', 'body04'}:
                raise ValueError('unknown reference role')
            path = Path(filename).expanduser().resolve(strict=True)
            if 'koreatest' in path.parts and (
                    role == 'selection' or args.purpose in {'candidate', 'draft'}):
                raise ValueError('koreatest cannot be a selection/candidate/draft input')
            refs.append(dict(role=role, path=str(path), sha256=sha256(path)))
        if args.purpose in {'face_angle', 'body_angle', 'motion'}:
            if not args.identity_lock:
                raise ValueError('identity-lock required')
            lock = json.loads(Path(args.identity_lock).read_text())
            if not isinstance(lock, dict) or set(lock) != {'schema', 'face01', 'body04', 'memory_points_zh'}:
                raise ValueError('identity-lock keys invalid')
            if type(lock['schema']) is not int or lock['schema'] != 1:
                raise ValueError('identity-lock schema must be 1')
            points = lock['memory_points_zh']
            if not isinstance(points, list) or len(points) != 2 or not all(isinstance(x, str) and x.strip() for x in points):
                raise ValueError('identity-lock requires two memory points')
            for role in ('face01', 'body04'):
                entry = lock[role]
                if not isinstance(entry, dict) or set(entry) != {'path', 'sha256'}:
                    raise ValueError('identity-lock ' + role + ' keys invalid')
                if not isinstance(entry['path'], str) or not Path(entry['path']).is_absolute():
                    raise ValueError('identity-lock path must be absolute')
                if not isinstance(entry['sha256'], str) or not re.fullmatch(r'[0-9a-f]{64}', entry['sha256']):
                    raise ValueError('identity-lock sha256 invalid')
            expected = [dict(role=role, **lock[role]) for role in ('face01', 'body04')]
            if refs != expected:
                raise ValueError('identity-lock reference count/order/path/hash mismatch')
    except (OSError, ValueError, TypeError) as exc:
        parser.error(str(exc))
    root = Path(args.run_dir).expanduser().resolve()
    call = root / args.id
    if call.exists():
        parser.error('call id already exists; use a new id for every attempt')
    call.mkdir(parents=True)
    prompt_sent = call / 'prompt-sent.txt'
    prompt_sent.write_bytes(HOST_PREFIX.encode('utf-8') + b'\n' +
                            '请求：'.encode('utf-8') + prompt.read_bytes())
    argv = ['codex', 'exec', '--skip-git-repo-check', '--ephemeral', '-s',
            'workspace-write', '-C', str(call), '--disable', 'plugins', '--json',
            '-o', str(call / 'last-message.txt')]
    for ref in refs:
        argv += ['-i', ref['path']]
    argv += ['-']
    request = dict(id=args.id, task=args.task, purpose=args.purpose,
                   attempt=int(args.id.rsplit('-', 1)[-1]) if args.id.rsplit('-', 1)[-1].isdigit() else 1,
                   codex_cli_version=CLI_VERSION, refs=refs, prompt_path=str(prompt),
                   prompt_sha256=prompt_hash, prompt_sent_path=str(prompt_sent),
                   prompt_sent_sha256=sha256(prompt_sent), argv=argv, run_dir=str(root),
                   output_path=str(call / (args.id + '.png')), started_at=now())
    (call / 'request.json').write_text(json.dumps(request, ensure_ascii=False, indent=2) + '\n')
    print(shlex.join(argv) + ' < ' + shlex.quote(str(prompt_sent)) +
          ' > ' + shlex.quote(str(call / 'events.jsonl')))


if __name__ == '__main__':
    main()
