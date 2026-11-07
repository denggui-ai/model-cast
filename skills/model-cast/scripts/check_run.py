"""Verify PNG receipts or crop provenance and current source/reference hashes."""
import argparse
import json
from pathlib import Path

from collect_receipt import dimensions, size_ok
from gen_request import sha256


def check(root):
    root = root.resolve()
    problems = []
    covered = set()
    output_hashes = {}
    for path in sorted(root.rglob('receipt.json')):
        try:
            receipt = json.loads(path.read_text())
            for ref in receipt['refs']:
                if sha256(ref['path']) != ref['sha256']:
                    problems.append(f'{path}: reference hash mismatch: {ref["path"]}')
            outputs = receipt.get('outputs')
            if outputs is None:  # T0 legacy receipts
                outputs = [receipt] if receipt.get('output_path') else []
            output_hashes[path.parent.resolve()] = {o['output_sha256'] for o in outputs}
            for output in outputs:
                image = Path(output['output_path']).resolve()
                covered.add(image)
                if sha256(image) != output['output_sha256']:
                    problems.append(f'{image}: output hash mismatch')
                width, height = dimensions(image)
                if (width, height) != (output['width'], output['height']):
                    problems.append(f'{image}: recorded dimensions mismatch')
                if not size_ok(receipt['purpose'], width, height):
                    problems.append(f'{image}: size_fail')
        except (OSError, ValueError, KeyError, TypeError) as exc:
            problems.append(f'{path}: {exc}')
    for image in sorted(root.rglob('*.png')):
        external_path = image.parent / 'EXTERNAL.json'
        if external_path.exists():
            try:
                entries = json.loads(external_path.read_text())['entries']
                entry = next((e for e in entries if e['file'] == image.name), None)
                if entry is not None:
                    if sha256(image) != entry['sha256']:
                        problems.append(f'{image}: external hash mismatch')
                    continue
            except (OSError, ValueError, KeyError, TypeError) as exc:
                problems.append(f'{external_path}: {exc}')
        crop_path = Path(str(image) + '.crop.json')
        sheet_path = Path(str(image) + '.sheet.json')
        if sheet_path.exists():
            try:
                sheet = json.loads(sheet_path.read_text())
                if not sheet['sources']:
                    raise ValueError('empty sheet sources')
                for source in sheet['sources']:
                    if sha256(source['path']) != source['sha256']:
                        problems.append(f'{image}: source hash mismatch')
                if sha256(image) != sheet['output_sha256']:
                    problems.append(f'{image}: output hash mismatch')
            except (OSError, ValueError, KeyError, TypeError) as exc:
                problems.append(f'{sheet_path}: {exc}')
        elif crop_path.exists():
            try:
                crop = json.loads(crop_path.read_text())
                if sha256(crop['source_path']) != crop['source_sha256']:
                    problems.append(f'{image}: source hash mismatch')
                if sha256(image) != crop['output_sha256']:
                    problems.append(f'{image}: output hash mismatch')
                if dimensions(image) != (crop['width'], crop['height']):
                    problems.append(f'{image}: recorded dimensions mismatch')
            except (OSError, ValueError, KeyError, TypeError) as exc:
                problems.append(f'{crop_path}: {exc}')
        elif image.resolve() not in covered:
            try:
                call_dir = image.parent
                while call_dir != root and not (call_dir / 'receipt.json').exists():
                    call_dir = call_dir.parent
                if sha256(image) not in output_hashes.get(call_dir.resolve(), set()):
                    problems.append(f'{image}: missing receipt')
            except OSError as exc:
                problems.append(f'{image}: {exc}')
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', required=True)
    args = parser.parse_args()
    root = Path(args.run_dir).expanduser().resolve()
    problems = check(root) if root.is_dir() else ['run directory does not exist']
    for problem in problems:
        print(problem)
    print(f'{len(problems)} problems')
    return int(bool(problems))


if __name__ == '__main__':
    raise SystemExit(main())
