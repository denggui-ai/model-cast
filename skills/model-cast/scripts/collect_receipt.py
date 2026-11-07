"""Collect only the thread.started session's new PNGs; retain all outputs."""
import argparse
import json
from pathlib import Path
import re
import shutil
import struct

from gen_request import now, sha256


def dimensions(path):
    with Path(path).open('rb') as stream:
        header = stream.read(24)
    if len(header) != 24 or header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR':
        raise ValueError('invalid PNG header: ' + str(path))
    width, height = struct.unpack('>II', header[16:24])
    if not width or not height:
        raise ValueError('zero PNG dimension')
    return width, height


def size_ok(purpose, width, height):
    if purpose == 't0':
        return True
    if purpose in {'face01', 'face_angle'}:
        return width >= 1024 and height >= 1024
    short = min(width, height)
    if purpose in {'draft', 'diagram'}:
        return short >= 1024
    if purpose in {'candidate', 'motion'}:
        return short >= 1024 and height >= width
    return short >= 1024 and height > width


def new_images(events_path, before_path):
    events = [json.loads(line) for line in Path(events_path).read_text().splitlines() if line.strip()]
    threads = {e['thread_id'] for e in events if e.get('type') == 'thread.started'}
    if len(threads) != 1:
        raise ValueError('expected one thread.started.thread_id')
    thread = threads.pop()
    if not isinstance(thread, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', thread):
        raise ValueError('invalid thread_id')
    lines = Path(before_path).read_text().splitlines()
    if not lines or not any(line.strip() for line in lines):
        raise ValueError('before snapshot missing or empty')
    before = set()
    for line in lines:
        if not line.strip():
            continue
        path = Path(line)
        if not path.is_absolute():
            raise ValueError('before snapshot must contain absolute paths')
        before.add(path)
    directory = Path.home() / '.codex' / 'generated_images' / thread
    # Never enumerate sibling session directories. T0 events contain no image paths.
    return sorted(path for path in directory.glob('*.png') if path not in before)


def contaminated_commands(events_path):
    commands = []
    for line in Path(events_path).read_text().splitlines():
        if not line.strip():
            continue
        item = json.loads(line).get('item', {})
        if item.get('type') != 'command_execution':
            continue
        command = item.get('command', '')
        # Remove only the allowed path, so a second SKILL.md still contaminates.
        other_skills = command.replace('~/.codex/skills/.system/imagegen/SKILL.md', '')
        other_skills = other_skills.replace('/.codex/skills/.system/imagegen/SKILL.md', '')
        if '/plugins/' in command or 'SKILL.md' in other_skills:
            if command not in commands:
                commands.append(command)
    return commands


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', required=True)
    parser.add_argument('--before', required=True)
    parser.add_argument('--exit-code', required=True, type=int)
    parser.add_argument('--events', required=True)
    args = parser.parse_args()
    request_path = Path(args.request).resolve()
    request = json.loads(request_path.read_text())
    receipt_path = request_path.parent / 'receipt.json'
    ledger = Path(request['run_dir']) / 'quota.jsonl'
    if receipt_path.exists():
        parser.error('receipt already exists; refusing duplicate accounting')
    if ledger.exists():
        if any(json.loads(line).get('id') == request['id'] for line in ledger.read_text().splitlines() if line.strip()):
            parser.error('id already accounted in quota')
    receipt = {key: request[key] for key in ('id', 'task', 'purpose', 'attempt',
               'codex_cli_version', 'refs', 'prompt_path', 'prompt_sha256', 'argv', 'started_at')}
    for key in ('prompt_sent_path', 'prompt_sent_sha256'):
        if key in request:
            receipt[key] = request[key]
    receipt.update(finished_at=request.get('finished_at', now()), exit_code=args.exit_code, status='tool_error',
                   images_generated=0, outputs=[], failure_class=5, note='', contamination=[])
    for key in ('source_generated_path', 'output_path', 'output_sha256', 'width', 'height'):
        receipt[key] = None
    try:
        receipt['contamination'] = contaminated_commands(args.events)
        images = new_images(args.events, args.before)
        receipt['images_generated'] = len(images)
        for index, source in enumerate(images, 1):
            destination = (request_path.parent / (request['id'] + '-' + str(index) + '.png')
                           if len(images) > 1 else Path(request['output_path']))
            shutil.copy2(source, destination)
            output = dict(output_path=str(destination), output_sha256=sha256(destination),
                          source_generated_path=str(source), width=None, height=None)
            receipt['outputs'].append(output)
        for output in receipt['outputs']:
            output['width'], output['height'] = dimensions(output['output_path'])
        if args.exit_code:
            receipt['note'] = 'host command exited nonzero'
        elif receipt['contamination']:
            receipt['status'] = 'contaminated'
        elif len(images) == 0:
            receipt['status'] = 'no_image'
        elif len(images) > 1:
            receipt['status'] = 'multi_image'
        elif not size_ok(request['purpose'], **{k: receipt['outputs'][0][k] for k in ('width', 'height')}):
            receipt.update(status='size_fail', failure_class=6)
        else:
            receipt.update(receipt['outputs'][0])
            receipt.update(status='ok', failure_class=None)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        receipt['note'] = str(exc)
    serialized = json.dumps(receipt, ensure_ascii=False)
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    with ledger.open('a') as stream:
        stream.write(serialized + '\n')
    print(serialized)


if __name__ == '__main__':
    main()
