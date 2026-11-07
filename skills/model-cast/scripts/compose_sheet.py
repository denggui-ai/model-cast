"""Compose labeled PNG sheets without generation or quota use.

Labels are laid out verbatim (wrapped to the cell width); nothing is invented.
A CJK-capable host font is required: missing glyphs are an error, never boxes.
"""
import argparse
import json
import math
import unicodedata
from pathlib import Path
from gen_request import sha256

# Host fonts only; nothing is installed. First existing file that covers every label glyph wins.
FONT_CANDIDATES = (
    '/System/Library/Fonts/Hiragino Sans GB.ttc',
    '/System/Library/Fonts/STHeiti Medium.ttc',
    '/System/Library/Fonts/PingFang.ttc',
    '/Library/Fonts/Arial Unicode.ttf',
    '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
)
FONT_SIZE = 20
PAD = 5
NOT_A_GLYPH = '\U0010FFFD'  # private-use code point: renders as the font's missing-glyph shape


def missing_glyphs(font, text):
    """Characters the font draws with its fallback (tofu) shape."""
    tofu = font.getmask(NOT_A_GLYPH)
    tofu_key = (tofu.size, bytes(tofu))
    missing = []
    for ch in sorted(set(text)):
        if ch.isspace():
            continue
        mask = font.getmask(ch)
        if (mask.size, bytes(mask)) == tofu_key:
            missing.append(ch)
    return missing


def pick_font(ImageFont, labels, explicit=None):
    candidates = [explicit] if explicit else list(FONT_CANDIDATES)
    text = ''.join(labels)
    tried = []
    for path in candidates:
        if not Path(path).is_file():
            tried.append(path + ' (absent)')
            continue
        font = ImageFont.truetype(path, FONT_SIZE)
        missing = missing_glyphs(font, text)
        if not missing:
            return font, path
        tried.append(path + ' (missing ' + ''.join(missing[:10]) + ')')
    raise ValueError('tool-blocked: no host font covers the label glyphs; tried: ' + '; '.join(tried))


def tokens(paragraph):
    """Words (incl. symbols like 45°) stay whole; each wide CJK character and each space is its own token."""
    out, word = [], ''
    for ch in paragraph:
        if not ch.isspace() and unicodedata.east_asian_width(ch) not in ('W', 'F'):
            word += ch
            continue
        if word:
            out.append(word)
            word = ''
        out.append(ch)
    if word:
        out.append(word)
    return out


def wrap(draw, font, label, width):
    """Wrap to the cell width; explicit newlines are kept; overlong words break by character."""
    lines = []
    for paragraph in label.split('\n'):
        line = ''
        for token in tokens(paragraph):
            trial = line + token
            if draw.textlength(trial, font=font) <= width:
                line = trial
                continue
            if line.strip():
                lines.append(line.rstrip())
            line = '' if token.isspace() else token
            while draw.textlength(line, font=font) > width:
                cut = len(line)
                while cut > 1 and draw.textlength(line[:cut], font=font) > width:
                    cut -= 1
                if draw.textlength(line[:cut], font=font) > width:
                    raise ValueError('cell too narrow for one character of label: ' + repr(label))
                lines.append(line[:cut])
                line = line[cut:]
        lines.append(line)
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    parser.add_argument('--cols', required=True, type=int)
    parser.add_argument('--cell', required=True)
    parser.add_argument('--item', action='append', required=True, help='PATH=LABEL; use \\n in LABEL for a forced line break')
    parser.add_argument('--font', help='explicit host font file (overrides the candidate list)')
    args = parser.parse_args()
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        parser.error('tool-blocked: Pillow unavailable')
    out = Path(args.out).resolve()
    record = Path(str(out) + '.sheet.json')
    try:
        w, h = map(int, args.cell.lower().split('x'))
        if w < 1 or h < 1 or args.cols < 1:
            raise ValueError('cell and cols must be positive')
        if out.suffix.lower() != '.png' or out.exists() or record.exists():
            raise ValueError('output must be a new .png')
        items = []
        for item in args.item:
            path, label = item.rsplit('=', 1)
            items.append((Path(path).expanduser().resolve(strict=True), label.replace('\\n', '\n')))
        font, font_path = pick_font(ImageFont, [label for _, label in items], args.font)
        measure = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        wrapped = [wrap(measure, font, label, w - 2 * PAD) for _, label in items]
        ascent, descent = font.getmetrics()
        line_h = ascent + descent + 2
        label_h = max(len(lines) for lines in wrapped) * line_h + 2 * PAD
        rows = math.ceil(len(items) / args.cols)
        canvas = Image.new('RGB', (w * args.cols, (h + label_h) * rows), 'white')
        draw = ImageDraw.Draw(canvas)
        sources = []
        for i, ((path, label), lines) in enumerate(zip(items, wrapped)):
            if path == out:
                raise ValueError('output cannot be a source')
            sources.append(dict(path=str(path), sha256=sha256(path), label=label))
            with Image.open(path) as source:
                thumb = source.convert('RGB')
                thumb.thumbnail((w, h))
                x, y = (i % args.cols) * w, (i // args.cols) * (h + label_h)
                canvas.paste(thumb, (x + (w - thumb.width) // 2, y + (h - thumb.height) // 2))
                for n, line in enumerate(lines):
                    draw.text((x + PAD, y + h + PAD + n * line_h), line, font=font, fill='black')
        out.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out, format='PNG')
        record.write_text(json.dumps(dict(sources=sources, output_sha256=sha256(out), font=font_path),
                                     ensure_ascii=False, indent=2) + '\n')
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(out)


if __name__ == '__main__':
    main()
