"""Lay out a formal model card from original images only (no generation, no quota).

Content comes verbatim from a card spec JSON (texts are written by the host from real records).
Memory-point close-ups must be crop.py outputs of the main face; the main face itself carries no boxes.
Writes OUT.png plus OUT.png.sheet.json (same record format as compose_sheet, so check_run verifies it).
"""
import argparse
import json
import math
from pathlib import Path
from gen_request import sha256
from compose_sheet import missing_glyphs, pick_font, tokens

UNIT = 8
W, M, GAP = 2000, 12 * UNIT, 4 * UNIT
THEMES = {
    'cream': dict(paper='#F4EFE7', panel='#FBF8F3', tint='#F1E9DF', ink='#3A2F2A',
                  muted='#6F6056', accent='#704034', rule='#D9CEC1'),
    'ink': dict(paper='#F4F5F1', panel='#FDFEFA', tint='#E9EEE7', ink='#23312D',
                muted='#59635D', accent='#23483F', rule='#CED7CE'),
}
NO_LINE_START = '，。、；：！？…—）》」』】〕〉”’.,;:!?)]}°%'
NO_LINE_END = '（《「『【〔〈“‘([{'
SPEC_KEYS = {'schema', 'name', 'card_type', 'tags', 'face', 'profile', 'recognize',
             'turnaround', 'positioning', 'reasons', 'rules', 'footer'}


def contrast_ratio(first, second):
    """WCAG relative luminance for the solid sRGB colors used by the card."""
    def luminance(color):
        channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in channels]
        return sum(c * weight for c, weight in zip(linear, (.2126, .7152, .0722)))
    low, high = sorted((luminance(first), luminance(second)))
    return (high + .05) / (low + .05)


def load_spec(path):
    spec = json.loads(Path(path).read_text(encoding='utf-8'))

    def obj(value, keys, where):
        if not isinstance(value, dict) or set(value) != set(keys):
            raise ValueError(f'{where} keys must be {sorted(keys)}')

    def string(value, where):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'{where} must be nonempty text')

    def sequence(value, where, count=None):
        if not isinstance(value, list) or (count is not None and len(value) != count):
            raise ValueError(f'{where} must be a list' + (f' of exactly {count} items' if count is not None else ''))

    def strings(value, where, count=None):
        sequence(value, where, count)
        for item in value: string(item, where)

    def text_object(value, keys, where):
        obj(value, keys, where)
        for key in keys: string(value[key], f'{where}.{key}')

    obj(spec, SPEC_KEYS, 'card spec')
    if type(spec['schema']) is not int or spec['schema'] != 2:
        raise ValueError('card spec schema must be 2; schema 1 is retired')
    for key in ('name', 'card_type', 'footer'): string(spec[key], key)
    strings(spec['tags'], 'tags', 3)
    text_object(spec['face'], ('path', 'label'), 'face')
    for key in ('profile', 'positioning'):
        fields = {'heading', 'rows'} | ({'note'} if key == 'profile' else set())
        obj(spec[key], fields, key)
        string(spec[key]['heading'], f'{key}.heading')
        sequence(spec[key]['rows'], f'{key}.rows')
        for row in spec[key]['rows']: strings(row, f'{key}.rows pair', 2)
    string(spec['profile']['note'], 'profile.note')
    obj(spec['recognize'], ('heading', 'details', 'tip'), 'recognize')
    for key in ('heading', 'tip'): string(spec['recognize'][key], f'recognize.{key}')
    sequence(spec['recognize']['details'], 'recognize.details', 2)
    for d in spec['recognize']['details']:
        text_object(d, ('path', 'title', 'label'), 'recognize.details item')
    obj(spec['turnaround'], ('heading', 'items'), 'turnaround')
    string(spec['turnaround']['heading'], 'turnaround.heading')
    sequence(spec['turnaround']['items'], 'turnaround.items', 4)
    for item in spec['turnaround']['items']:
        text_object(item, ('path', 'label'), 'turnaround.items item')
    obj(spec['reasons'], ('heading', 'label', 'points', 'note'), 'reasons')
    for key in ('heading', 'label', 'note'): string(spec['reasons'][key], f'reasons.{key}')
    sequence(spec['reasons']['points'], 'reasons.points', 5)
    for item in spec['reasons']['points']:
        text_object(item, ('title', 'text'), 'reasons.points item')
    obj(spec['rules'], ('heading', 'fixed_heading', 'fixed', 'variable_heading', 'variable', 'notes'), 'rules')
    for key in ('heading', 'fixed_heading', 'variable_heading'): string(spec['rules'][key], f'rules.{key}')
    for key in ('fixed', 'variable', 'notes'): strings(spec['rules'][key], f'rules.{key}')
    if not 1 <= len(spec['rules']['notes']) <= 3:
        raise ValueError('rules.notes must contain 1 to 3 items')

    # Keep the crop.py source and output hash gates before any rendering or output writes.
    face = Path(spec['face']['path']).resolve(strict=True)
    for d in spec['recognize']['details']:
        crop = json.loads(Path(str(Path(d['path']).resolve(strict=True)) + '.crop.json').read_text())
        if Path(crop['source_path']).resolve() != face or crop['source_sha256'] != sha256(face):
            raise ValueError('close-up is not a crop.py output of the main face: ' + d['path'])
        if crop['output_sha256'] != sha256(d['path']): raise ValueError('close-up changed after cropping: ' + d['path'])
        d['box'] = crop['box']
    return spec


def fit(Image, path, box, upscale=False):
    with Image.open(path) as source:
        image = source.convert('RGB')
    if upscale:
        scale = min(box[0] / image.width, box[1] / image.height)
        image = image.resize((max(1, round(image.width * scale)), max(1, round(image.height * scale))),
                             Image.Resampling.LANCZOS)
    else:
        image.thumbnail(box)
    return image


def all_text(spec):
    parts = [spec['name'], spec['card_type'], *spec['tags'], spec['face']['label'], spec['footer']]
    for key in ('profile', 'positioning'):
        parts.append(spec[key]['heading'])
        for row in spec[key]['rows']: parts.extend(row)
    parts += [spec['profile']['note'], spec['recognize']['heading'], spec['recognize']['tip']]
    for d in spec['recognize']['details']: parts += [d['title'], d['label']]
    parts += [spec['turnaround']['heading']] + [t['label'] for t in spec['turnaround']['items']]
    parts += [spec['reasons'][key] for key in ('heading', 'label', 'note')]
    for point in spec['reasons']['points']: parts += [point['title'], point['text']]
    parts += [spec['rules']['heading'], spec['rules']['fixed_heading'], *spec['rules']['fixed'],
              spec['rules']['variable_heading'], *spec['rules']['variable'], *spec['rules']['notes']]
    return parts


def wrap(draw, font, label, width):
    """Keep punctuation attached, avoid lone Chinese endings, and retain paragraphs."""
    def joined(parts):
        units = []
        for part in parts:
            if units and (part[0] in NO_LINE_START or units[-1][-1] in NO_LINE_END):
                units[-1] += part
            else:
                units.append(part)
        return units

    lines = []
    for paragraph in label.split('\n'):
        start = len(lines)
        line = ''
        for unit in joined(tokens(paragraph)):
            # Only an overlong word is split, and its punctuation remains attached.
            pieces = [unit] if draw.textlength(unit, font=font) <= width else joined(unit)
            for piece in pieces:
                if draw.textlength(piece, font=font) > width:
                    raise ValueError('card column too narrow for text: ' + repr(piece))
                if draw.textlength(line + piece, font=font) > width:
                    lines.append(line.rstrip())
                    line = ''
                if line or not piece.isspace():
                    line += piece
        lines.append(line.rstrip())
        ending = lines[-1].strip(NO_LINE_START + NO_LINE_END)
        if len(lines) > start + 1 and len(ending) == 1 and '\u3400' <= ending <= '\u9fff':
            previous = joined(tokens(lines[-2]))
            # Move the preceding character with any attached punctuation/word.
            # Only pull back a CJK unit: a Latin word was followed by a space that rstrip() already dropped.
            if len(previous) > 1 and '㐀' <= previous[-1].strip(NO_LINE_START + NO_LINE_END)[:1] <= '鿿':
                tail = previous[-1] + lines[-1]
                if draw.textlength(tail, font=font) <= width:
                    lines[-2] = ''.join(previous[:-1]).rstrip()
                    lines[-1] = tail
    return lines


def render(spec, out, theme='cream'):
    from PIL import Image, ImageDraw, ImageFont
    colors = THEMES[theme]
    for surface in ('paper', 'panel', 'tint'):
        for role, minimum in (('ink', 7), ('muted', 4.5), ('accent', 7)):
            if contrast_ratio(colors[role], colors[surface]) < minimum:
                raise ValueError(f'theme contrast too low: {theme} {role}/{surface}')
    ink, muted, accent = (colors[key] for key in ('ink', 'muted', 'accent'))
    paper, panel_color, tint, rule = (colors[key] for key in ('paper', 'panel', 'tint', 'rule'))
    texts = all_text(spec) + ['0123456789']
    regular, font_path = pick_font(ImageFont, texts)
    strong = regular
    # Use an installed weight of the selected family, never a substitute font.
    for index in range(1, 16):
        try:
            candidate = ImageFont.truetype(font_path, 20, index=index)
        except OSError:
            break
        family, style = candidate.getname()
        if family == regular.getname()[0] and style.lower() in ('w6', 'bold', 'semibold', 'demibold', 'medium'):
            missing = missing_glyphs(candidate, ''.join(texts))
            if missing:
                raise ValueError('tool-blocked: heading font missing glyphs: ' + ''.join(missing))
            strong = candidate
            break
    f = {size: regular.font_variant(size=size) for size in (24, 26, 28, 30)}
    b = {size: strong.font_variant(size=size) for size in (24, 26, 28, 36, 112)}
    measure = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    ops = []  # Measure first, then draw once at the content's actual height.
    pad, section_gap, key_w = GAP, 8 * UNIT, 24 * UNIT
    content_w = W - 2 * M

    def line_h(font): return math.ceil(sum(font.getmetrics()) * 1.5)
    def block(value, font, width): return wrap(measure, font, value, width)
    def height(value, font, width): return len(block(value, font, width)) * line_h(font)

    def ink_height(value, font, width):
        return max(i * line_h(font) + measure.textbbox((0, 0), line, font=font, anchor='lt')[3]
                   for i, line in enumerate(block(value, font, width)))

    def text(value, font, x, y, width, color=ink):
        for line in block(value, font, width):
            ops.append(('text', (x, y), line, font, color))
            y += line_h(font)
        return y

    def line(x0, y0, x1, y1, color=rule, weight=1):
        ops.append(('line', (x0, y0, x1, y1), color, weight))

    def panel(x, y, width, h, fill=panel_color):
        ops.append(('panel', (x, y, x + width, y + h), fill, rule, 12))

    def heading(number, value, x, y, width, draw=True):
        if draw:
            text(number, b[24], x, y + UNIT, 6 * UNIT, accent)
            text(value, b[36], x + 7 * UNIT, y, width - 7 * UNIT)
        return y + height(value, b[36], width - 7 * UNIT) + 3 * UNIT

    def pills(values, font, x, y, width, fill=panel_color, outline=rule, color=ink, draw=True):
        cx, row_h = x, 0
        for value in values:
            cw = min(width, math.ceil(max(measure.textlength(p, font=font) for p in value.split('\n'))) + 4 * UNIT)
            ch = ink_height(value, font, cw - 4 * UNIT) + 3 * UNIT
            if cx > x and cx + cw > x + width:
                cx, y, row_h = x, y + row_h + 2 * UNIT, 0
            if draw:
                ops.append(('panel', (cx, y, cx + cw, y + ch), fill, outline, min(24, ch // 2)))
                text(value, font, cx + 2 * UNIT, y + 1.5 * UNIT, cw - 4 * UNIT, color)
            cx += cw + 2 * UNIT
            row_h = max(row_h, ch)
        return y + row_h

    def table_heights(rows, width):
        return [max(height(k, f[26], key_w), height(v, f[30], width - key_w - 3 * UNIT)) + 4 * UNIT
                for k, v in rows]

    def table(rows, x, y, width, available=None):
        heights = table_heights(rows, width)
        extra = max(0, (available or 0) - sum(heights)) / max(1, len(rows))
        for i, ((key, value), rh) in enumerate(zip(rows, heights)):
            rh += extra
            # The profile can share the portrait's height; positioning keeps its natural spacing.
            cy = y + (rh - max(height(key, f[26], key_w), height(value, f[30], width - key_w - 3 * UNIT))) / 2
            text(key, f[26], x, cy + 2, key_w, muted)
            text(value, f[30], x + key_w + 3 * UNIT, cy, width - key_w - 3 * UNIT)
            y += rh
            if i < len(rows) - 1: line(x, y, x + width, y)
        return y

    def caption(value, x, y, width):
        prefix, separator, rest = value.partition(' ')
        if separator and prefix.isdigit() and rest:
            offset = math.ceil(measure.textlength(prefix + separator, font=b[24]))
            text(prefix, b[24], x, y, offset, accent)
            return text(rest, f[24], x + offset, y, width - offset, muted)
        return text(value, f[24], x, y, width, muted)

    # Masthead: all wording comes from name/card_type/tags, with no new descriptor.
    line(M, M, M + 8 * UNIT, M, accent, 4)
    y = M + 4 * UNIT
    type_w = math.ceil(measure.textlength(spec['card_type'], font=b[26]))
    name_w = content_w - type_w - 2 * GAP
    name_h = ink_height(spec['name'], b[112], name_w)
    text(spec['name'], b[112], M, y, name_w)
    text(spec['card_type'], b[26], W - M - type_w, y + name_h - ink_height(spec['card_type'], b[26], type_w), type_w, accent)
    y = pills(spec['tags'], f[24], M, y + name_h + GAP, content_w, color=muted) + GAP
    line(M, y, W - M, y)
    y += GAP

    # Main portrait and 01 profile occupy one equally high pair of panels.
    face_w = 104 * UNIT
    profile_x, profile_w = M + face_w + GAP, content_w - face_w - GAP
    face_size = face_w - 2 * pad
    face = fit(Image, spec['face']['path'], (face_size, face_size))
    face_caption_h = height(spec['face']['label'], f[24], face_size)
    face_h = 2 * pad + face_size + 3 * UNIT + face_caption_h
    profile = spec['profile']
    profile_inner = profile_w - 2 * pad
    profile_start = heading('01', profile['heading'], 0, 0, profile_inner, draw=False)
    note_h = height(profile['note'], f[24], profile_inner)
    profile_h = 2 * pad + profile_start + sum(table_heights(profile['rows'], profile_inner)) + GAP + note_h
    row_h = max(face_h, profile_h)
    panel(M, y, face_w, row_h)
    panel(profile_x, y, profile_w, row_h)
    photo_h = row_h - 2 * pad - 3 * UNIT - face_caption_h
    fx, fy = M + pad + (face_size - face.width) // 2, y + pad + (photo_h - face.height) // 2
    # Owner 2026-11-06: no boxes on the main face; the numbered close-ups carry the memory points.
    ops.append(('image', (fx, fy), face))
    caption(spec['face']['label'], M + pad, y + row_h - pad - face_caption_h, face_size)
    py = heading('01', profile['heading'], profile_x + pad, y + pad, profile_inner)
    note_y = y + row_h - pad - note_h
    table(profile['rows'], profile_x + pad, py, profile_inner, available=note_y - GAP - py)
    text(profile['note'], f[24], profile_x + pad, note_y, profile_inner, muted)
    y += row_h + section_gap

    # 02: two parallel, equal-height close-up cards. Images contain every source pixel.
    recognize = spec['recognize']
    y = heading('02', recognize['heading'], M, y, content_w)
    detail_w = (content_w - GAP) // 2
    photo_w = detail_w // 2
    label_w = detail_w - 2 * pad - photo_w - 3 * UNIT
    detail_images = [fit(Image, d['path'], (photo_w, W), upscale=True) for d in recognize['details']]
    detail_text_heights = [height(d['title'], b[28], label_w) + 2 * UNIT + height(d['label'], f[28], label_w)
                           for d in recognize['details']]
    group_h = max(*(img.height for img in detail_images), *detail_text_heights)
    detail_h = group_h + 2 * pad
    detail_text_y = y + pad + (group_h - max(detail_text_heights)) // 2
    for i, (detail, img) in enumerate(zip(recognize['details'], detail_images)):
        x = M + i * (detail_w + GAP)
        panel(x, y, detail_w, detail_h)
        ix, iy = x + pad, y + pad + (group_h - img.height) // 2
        ops.append(('image', (ix, iy), img))
        ops.append(('badge', (ix + UNIT, iy + UNIT), str(i + 1)))
        tx, ty = x + pad + photo_w + 3 * UNIT, detail_text_y
        ty = text(detail['title'], b[28], tx, ty, label_w, accent) + 2 * UNIT
        text(detail['label'], f[28], tx, ty, label_w)
    y = text(recognize['tip'], f[24], M, y + detail_h + 3 * UNIT, content_w, muted) + section_gap

    # 03: equal photo slots and captions on a shared baseline; no image cropping.
    turnaround = spec['turnaround']
    y = heading('03', turnaround['heading'], M, y, content_w)
    tw = (content_w - 3 * GAP) // 4
    photo_w, th = tw - 4 * UNIT, (tw - 4 * UNIT) * 3 // 2
    caption_h = max(height(t['label'], f[24], tw - 6 * UNIT) for t in turnaround['items'])
    turn_h = 2 * UNIT + th + 3 * UNIT + caption_h + 3 * UNIT
    for i, item in enumerate(turnaround['items']):
        x = M + i * (tw + GAP)
        panel(x, y, tw, turn_h)
        img = fit(Image, item['path'], (photo_w, th))
        ops.append(('image', (x + (tw - img.width) // 2, y + 2 * UNIT + (th - img.height) // 2), img))
        caption(item['label'], x + 3 * UNIT, y + 2 * UNIT + th + 3 * UNIT, tw - 6 * UNIT)
    y += turn_h + section_gap

    # 04: a compact information strip, with the same key width and fixed row padding.
    positioning = spec['positioning']
    inner = content_w - 2 * pad
    columns = max(1, min(3, len(positioning['rows'])))
    column_w = (inner - (columns - 1) * GAP) // columns
    row_groups = [positioning['rows'][i:i + columns] for i in range(0, len(positioning['rows']), columns)]
    group_heights = [max(table_heights(rows, column_w)) for rows in row_groups]
    position_start = heading('04', positioning['heading'], 0, 0, inner, draw=False)
    position_h = 2 * pad + position_start + sum(group_heights)
    panel(M, y, content_w, position_h)
    py = heading('04', positioning['heading'], M + pad, y + pad, inner)
    for rows, rh in zip(row_groups, group_heights):
        for i, row in enumerate(rows):
            x = M + pad + i * (column_w + GAP)
            table([row], x, py, column_w)
            if i < len(rows) - 1:
                line(x + column_w + GAP // 2, py + UNIT, x + column_w + GAP // 2, py + rh - UNIT)
        py += rh
    y += position_h + section_gap

    # 05: editorial label, five numbered casting notes, and a quiet closing note.
    reasons = spec['reasons']
    reason_start = heading('05', reasons['heading'], 0, 0, inner, draw=False)
    number_w, title_w = 7 * UNIT, 32 * UNIT
    body_w = inner - number_w - title_w - GAP
    point_heights = [max(height(p['title'], b[28], title_w), height(p['text'], f[28], body_w)) + 4 * UNIT
                     for p in reasons['points']]
    label_h = height(reasons['label'], f[24], inner)
    note_h = height(reasons['note'], f[24], inner)
    reason_h = 2 * pad + reason_start + label_h + 3 * UNIT + sum(point_heights) + 3 * UNIT + note_h
    panel(M, y, content_w, reason_h)
    rx = M + pad
    ry = heading('05', reasons['heading'], rx, y + pad, inner)
    ry = text(reasons['label'], f[24], rx, ry, inner, muted) + 3 * UNIT
    for i, (point, rh) in enumerate(zip(reasons['points'], point_heights), 1):
        text(str(i), b[24], rx, ry + 2 * UNIT + 2, number_w, accent)
        text(point['title'], b[28], rx + number_w, ry + 2 * UNIT, title_w, accent)
        text(point['text'], f[28], rx + number_w + title_w + GAP, ry + 2 * UNIT, body_w)
        ry += rh
        if i < len(point_heights): line(rx, ry, rx + inner, ry)
    text(reasons['note'], f[24], rx, ry + 3 * UNIT, inner, muted)
    y += reason_h + section_gap

    # 06: filled/outlined group labels, verbatim rule chips, and separate note bands.
    rules = spec['rules']
    rules_inner = content_w - 2 * pad
    half_w = (rules_inner - GAP) // 2
    rule_start = heading('06', rules['heading'], 0, 0, rules_inner, draw=False)
    group_heights = []
    for group in ('fixed', 'variable'):
        gy = pills([rules[group + '_heading']], b[26], 0, 0, half_w, draw=False) + 3 * UNIT
        group_heights.append(pills(rules[group], f[28], 0, gy, half_w, draw=False))
    note_heights = [height(note, f[24], rules_inner - 4 * UNIT) + 4 * UNIT for note in rules['notes']]
    notes_h = sum(note_heights) + (len(note_heights) - 1) * UNIT
    rules_h = 2 * pad + rule_start + max(group_heights) + GAP + notes_h
    panel(M, y, content_w, rules_h)
    gy = heading('06', rules['heading'], M + pad, y + pad, rules_inner)
    for i, group in enumerate(('fixed', 'variable')):
        x = M + pad + i * (half_w + GAP)
        by = pills([rules[group + '_heading']], b[26], x, gy, half_w,
                   fill=accent if i == 0 else panel_color, outline=accent, color=panel_color if i == 0 else accent) + 3 * UNIT
        pills(rules[group], f[28], x, by, half_w)
    ny = gy + max(group_heights) + GAP
    for note, note_band_h in zip(rules['notes'], note_heights):
        panel(M + pad, ny, rules_inner, note_band_h, tint)
        line(M + pad, ny + 2 * UNIT, M + pad, ny + note_band_h - 2 * UNIT, accent, 3)
        text(note, f[24], M + pad + 2 * UNIT, ny + 2 * UNIT, rules_inner - 4 * UNIT, muted)
        ny += note_band_h + UNIT
    y += rules_h + GAP
    line(M, y, W - M, y)
    y = text(spec['footer'], f[24], M, y + 3 * UNIT, content_w, muted)

    canvas = Image.new('RGB', (W, math.ceil(y + M)), paper)
    draw = ImageDraw.Draw(canvas)
    for op in ops:
        if op[0] == 'text': draw.text(op[1], op[2], font=op[3], fill=op[4], anchor='lt')
        elif op[0] == 'image':
            canvas.paste(op[2], op[1])
            x, iy = op[1]
            draw.rectangle((x, iy, x + op[2].width - 1, iy + op[2].height - 1), outline=rule, width=1)
        elif op[0] == 'panel': draw.rounded_rectangle(op[1], radius=op[4], fill=op[2], outline=op[3], width=1)
        elif op[0] == 'line': draw.line(op[1], fill=op[2], width=op[3])
        elif op[0] == 'box': draw.rounded_rectangle(op[1], radius=8, outline=accent, width=2)
        elif op[0] == 'badge':
            x, by = op[1]
            draw.ellipse((x, by, x + 36, by + 36), fill=accent)
            draw.text((x + 18, by + 18), op[2], font=b[24], fill=panel_color, anchor='mm')
    canvas.save(out, format='PNG')
    return font_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', required=True); parser.add_argument('--out', required=True)
    parser.add_argument('--theme', choices=tuple(THEMES), default='cream')
    args = parser.parse_args()
    try:
        from PIL import Image  # noqa: F401 -- dependency gate, no installation
    except ImportError:
        parser.error('tool-blocked: Pillow unavailable')
    out = Path(args.out).resolve(); record = Path(str(out) + '.sheet.json')
    try:
        if out.suffix.lower() != '.png' or out.exists() or record.exists():
            raise ValueError('output must be a new .png (versions are never overwritten)')
        spec_path = Path(args.spec).resolve(strict=True)
        spec = load_spec(spec_path)
        items = [spec['face']] + [dict(d, label=f"{d['title']}：{d['label']}") for d in spec['recognize']['details']] + spec['turnaround']['items']
        sources = [dict(path=str(Path(i['path']).resolve()), sha256=sha256(i['path']), label=i['label']) for i in items]
        if any(Path(s['path']) == out for s in sources): raise ValueError('output cannot be a source')
        out.parent.mkdir(parents=True, exist_ok=True)
        font = render(spec, out, args.theme)
        record.write_text(json.dumps(dict(sources=sources, output_sha256=sha256(out), font=font,
                                          card_spec=dict(path=str(spec_path), sha256=sha256(spec_path))),
                                     ensure_ascii=False, indent=2) + '\n')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(out)


if __name__ == '__main__':
    main()
