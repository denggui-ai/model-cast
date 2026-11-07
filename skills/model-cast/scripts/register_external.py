"""Register external PNG provenance without charging generation quota."""
import argparse
import json
from pathlib import Path

from collect_receipt import dimensions
from gen_request import now, sha256


def receipt_coverage(directory):
    covered = set()
    hashes = set()
    # Include receipts naming outputs in D and ancestor call receipts for copies.
    receipts = set(directory.rglob('receipt.json'))
    receipts.update(parent / 'receipt.json' for parent in (directory, *directory.parents)
                    if (parent / 'receipt.json').is_file())
    for path in receipts:
        receipt = json.loads(path.read_text())
        outputs = receipt.get('outputs')
        if outputs is None:
            outputs = [receipt] if receipt.get('output_path') else []
        covered.update(Path(o['output_path']).resolve() for o in outputs)
        if path.parent == directory or path.parent in directory.parents:
            hashes.update(o['output_sha256'] for o in outputs)
    return covered, hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dir', required=True)
    parser.add_argument('--kind', required=True, choices=('chatgpt-web', 'screenshot'))
    parser.add_argument('--source', required=True)
    parser.add_argument('--note', default='')
    parser.add_argument('--file', action='extend', nargs='+')
    args = parser.parse_args()
    try:
        directory = Path(args.dir).expanduser().resolve(strict=True)
        if not directory.is_dir():
            raise ValueError('--dir must be a directory')
        manifest = directory / 'EXTERNAL.json'
        data = json.loads(manifest.read_text()) if manifest.exists() else {'entries': []}
        entries = {entry['file']: entry for entry in data['entries']}
        if args.file:
            images = []
            for name in args.file:
                if Path(name).name != name or not name.endswith('.png'):
                    raise ValueError('--file must be a PNG filename in D')
                image = directory / name
                if not image.is_file():
                    raise ValueError('file does not exist: ' + name)
                images.append(image)
        else:
            covered, hashes = receipt_coverage(directory)
            images = [image for image in sorted(directory.glob('*.png'))
                      if image.resolve() not in covered
                      and not Path(str(image) + '.crop.json').exists()
                      and sha256(image) not in hashes]
        added = 0
        for image in images:
            digest = sha256(image)
            if image.name in entries:
                if entries[image.name]['sha256'] != digest:
                    raise ValueError('external hash mismatch: ' + image.name)
                continue
            width, height = dimensions(image)
            entry = dict(file=image.name, sha256=digest, width=width, height=height,
                         kind=args.kind, source=args.source, note=args.note,
                         counts_quota=False, registered_at=now())
            data['entries'].append(entry)
            entries[image.name] = entry
            added += 1
        if added or not manifest.exists():
            manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(f'registered={added} skipped={len(images) - added}')


if __name__ == '__main__':
    main()
