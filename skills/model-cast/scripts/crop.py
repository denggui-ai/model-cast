"""Crop without resizing using macOS sips; retain hash-linked provenance."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile

from collect_receipt import dimensions
from gen_request import sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--src', required=True)
    parser.add_argument('--box', required=True, help='x0,y0,x1,y1; exclusive right/bottom')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    try:
        source = Path(args.src).expanduser().resolve(strict=True)
        output = Path(args.out).expanduser().absolute()
        record = Path(str(output) + '.crop.json')
        if output.exists() or record.exists():
            raise ValueError('output or crop record already exists; refusing overwrite')
        box = [int(value) for value in args.box.split(',')]
        if len(box) != 4:
            raise ValueError('box must contain four integers')
        x0, y0, x1, y1 = box
        info = subprocess.run(['/usr/bin/sips', '-g', 'pixelWidth', '-g', 'pixelHeight',
                               str(source)], check=True, capture_output=True, text=True)
        width = int(re.search(r'pixelWidth: (\d+)', info.stdout)[1])
        height = int(re.search(r'pixelHeight: (\d+)', info.stdout)[1])
        if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
            raise ValueError('crop box out of bounds')
        source_hash = sha256(source)
        output.parent.mkdir(parents=True, exist_ok=True)
        # Intermediate files stay beside the requested output, never in system tmp.
        with tempfile.TemporaryDirectory(prefix='.crop-', dir=output.parent) as directory:
            cropped = Path(directory) / 'crop.png'
            subprocess.run(['/usr/bin/sips', '--cropToHeightWidth', str(y1 - y0),
                            str(x1 - x0), '--cropOffset', str(y0), str(x0),
                            '-s', 'format', 'png', str(source), '--out', str(cropped)],
                           check=True, capture_output=True, text=True)
            if dimensions(cropped) != (x1 - x0, y1 - y0):
                raise ValueError('unexpected crop dimensions')
            metadata = dict(source_path=str(source), source_sha256=source_hash, box=box,
                            output_sha256=sha256(cropped), width=x1 - x0, height=y1 - y0)
            with output.open('xb') as stream:
                stream.write(cropped.read_bytes())
            with record.open('x') as stream:
                stream.write(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
    except (OSError, ValueError, TypeError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
