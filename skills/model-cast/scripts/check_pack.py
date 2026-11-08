"""Check V3 package structure, four upload files and exact original bytes, not visual identity."""
import argparse
import json
from pathlib import Path
from gen_request import sha256
from pack_common import (ANGLES, IDS, LANGS, SELLER, UPLOAD_IDS, ai_library_assets, ai_library_index,
                         display_hashes, engineering_layout, internal_hashes, joined_text,
                         load_manifest, names, seller_layout, verify_sources, version_manifest_name)


def tree(root):
    files = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() or p.is_symlink()}
    dirs = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_dir() and not p.is_symlink()}
    return files, dirs


def expected_dirs(paths):
    return {str(p) for name in paths for p in Path(name).parents if str(p) != '.'}


def check_seller(pack, m, lang, internal, problems):
    where = pack.name
    if not pack.is_dir(): problems.append('missing package: '+where); return
    expected = seller_layout(m, lang)
    actual, actual_dirs = tree(pack)
    for name in sorted(set(expected)-actual): problems.append(where+': missing: '+name)
    for name in sorted(actual-set(expected)): problems.append(where+': unexpected/internal file: '+name)
    dirs = expected_dirs(expected)
    for name in sorted(dirs-actual_dirs): problems.append(where+': missing directory: '+name)
    for name in sorted(actual_dirs-dirs): problems.append(where+': unexpected directory: '+name)
    upload = SELLER[lang]['folders'][1]+'/'
    forbidden = display_hashes(m)
    for name in sorted(actual):
        file = pack/name
        try:
            if file.is_symlink(): problems.append(where+': symlink: '+name); continue
            digest = sha256(file)
            if digest in internal: problems.append(where+': internal evidence content in package: '+name)
            if name.startswith(upload) and digest in forbidden:
                problems.append(where+': display/lifestyle image in upload folder: '+name)
            spec = expected.get(name)
            if not spec: continue
            if spec[0] == 'copy':
                if digest != (spec[2] or sha256(spec[1])): problems.append(where+': hash mismatch: '+name)
                if spec[2] is None and file.suffix.lower() in ('.txt','.md') and not file.read_text(encoding='utf-8').strip():
                    problems.append(where+': empty text: '+name)
            elif spec[0] == 'text':
                if file.read_text(encoding='utf-8') != joined_text(spec[1]): problems.append(where+': text differs from sources: '+name)
            elif spec[0] == 'json':
                if json.loads(file.read_text(encoding='utf-8')) != spec[1]: problems.append(where+': JSON differs from generated asset index: '+name)
        except (OSError, ValueError) as e: problems.append(where+': '+name+': '+str(e))
    lifestyle = pack/SELLER[lang]['folders'][2]
    if len(list(lifestyle.glob('*.png'))) != 3: problems.append(where+': lifestyle must contain exactly 3 PNGs')


LOOKSET_IMAGES = ['references/01.png'] + [f'supplements/{i}.png' for i in IDS]
LOOKSET_TEXTS = ['model.json', 'README.md']


def check_lookset(root, m, problems):
    """D2 must be exactly the vendor layout: P3-2 as the reference, the 12 originals as supplements.

    model.json/README.md are vendor output (validate echoes model.json into RUN), so only the file set is checked.
    """
    files, _ = tree(root)
    expected = set(LOOKSET_IMAGES) | set(LOOKSET_TEXTS)
    for name in sorted(expected - files): problems.append('Lookset missing: '+name)
    for name in sorted(files - expected): problems.append('Lookset unexpected file: '+name)
    allowed = {a['sha256'] for a in m['originals'].values()}; forbidden = display_hashes(m); refs = []
    try:
        for name in LOOKSET_IMAGES:
            file = root/name
            if file.is_symlink(): problems.append('Lookset symlink: '+name); continue
            if not file.is_file(): continue
            digest = sha256(file); refs.append(digest)
            if digest not in allowed or digest in forbidden: problems.append('Lookset non-original image: '+name)
        if len(refs) == len(LOOKSET_IMAGES):
            want = [m['originals']['P3-2']['sha256']] + sorted(m['originals'][i]['sha256'] for i in IDS)
            if [refs[0]] + sorted(refs[1:]) != want: problems.append('Lookset images are not exactly P3-2 + originals 01-12')
    except OSError as e: problems.append('Lookset: '+str(e))


CARD_SOURCES = 7


def check_card(m, problems):
    """Each identity card must be laid out only from originals or untouched crop.py crops of an original."""
    originals = {a['sha256']: a['path'] for a in m['originals'].values()}
    for lang in LANGS:
        card = m['identity_card'][lang]; where = 'identity_card.'+lang
        try:
            sheet_path = Path(card['path']+'.sheet.json')
            sheet = json.loads(sheet_path.read_text())
            if sheet['output_sha256'] != card['sha256']: problems.append(where+': sheet record does not match the card'); continue
            if card['sha256'] in {a['sha256'] for a in m['motion'].values()} | {m['diagram']['sha256']}:
                problems.append(where+': card is a lifestyle image or the diagram'); continue
            if len(sheet['sources']) != CARD_SOURCES:
                problems.append(where+f': card must list {CARD_SOURCES} sources (face, 2 close-ups, 4 turnaround), got {len(sheet["sources"])}'); continue
            for source in sheet['sources']:
                path = Path(source['path'])
                if not path.is_absolute(): path = sheet_path.parent/path
                digest = sha256(path)
                if digest != source['sha256']: problems.append(where+': source changed: '+str(path)); continue
                if digest in originals: continue
                crop_path = Path(str(path)+'.crop.json')
                crop = json.loads(crop_path.read_text()) if crop_path.is_file() else None
                if not crop or crop['source_sha256'] not in originals or crop['output_sha256'] != digest or not same_crop(originals[crop['source_sha256']], crop['box'], path):
                    problems.append(where+': source is not an original or an exact crop of one: '+str(path))
        except (OSError, ValueError, KeyError, TypeError) as e:
            problems.append(where+': card provenance unreadable: '+str(e))


def same_crop(original, box, crop):
    from PIL import Image
    with Image.open(original) as a, Image.open(crop) as b:
        expected = a.convert('RGB').crop(tuple(box))
        return b.size == expected.size == (box[2]-box[0], box[3]-box[1]) and expected.tobytes() == b.convert('RGB').tobytes()


def check_version_manifest(out, m, problems):
    """The RUN/c8 version manifest must describe what is actually in the packages."""
    path = Path(m['run_dir'])/'c8'/version_manifest_name(m)
    try:
        data = json.loads(path.read_text())
        recorded = {(r['package'], r['path']): r['sha256'] for r in data['files']}
        n = names(m)
        expected = {(n[lang], dest) for lang in LANGS for dest in seller_layout(m, lang)}
        expected |= {(n['engineering'], dest) for dest,spec in engineering_layout(m).items() if spec[0] == 'copy'}
        if set(recorded) != expected: problems.append('version manifest file list differs from the layout')
        for (package, dest), digest in sorted(recorded.items()):
            file = out/package/dest
            if not file.is_file() or sha256(file) != digest: problems.append('version manifest is stale for: '+package+'/'+dest)
        want = [dict(filename=f'{i}_{ANGLES[i]}.png', sha256=m['originals'][i]['sha256']) for i in UPLOAD_IDS]
        if data['upload_files'] != want: problems.append('version manifest upload files are stale')
        library_want = [dict(filename=filename, sha256=asset['sha256']) for filename,asset,_,_ in ai_library_assets(m)]
        if data.get('ai_library_files') != library_want: problems.append('version manifest AI library files are stale')
        for lang in LANGS:
            library = pack = out/n[lang]/('4_完整AI资料库（多文件上传）' if lang == 'zh' else '4_AI_Model_Library_MultiUpload')
            try:
                index = json.loads((library/'asset-index.json').read_text(encoding='utf-8'))
                if index != ai_library_index(m): problems.append(n[lang]+': asset-index.json is stale')
                if len(index.get('images',[])) != 16: problems.append(n[lang]+': AI library must index exactly 16 images')
            except (OSError,ValueError,TypeError) as e:
                problems.append(n[lang]+': AI library index unreadable: '+str(e))
    except (OSError, ValueError, KeyError, TypeError) as e:
        problems.append('version manifest unreadable: '+str(e))


def check(out_dir, m, manifest_path=None, require_lookset=False):
    out = Path(out_dir); n = names(m); problems = []
    try: verify_sources(m)
    except (OSError, ValueError) as e: problems.append(str(e))
    internal = set()
    try: internal = internal_hashes(m)
    except (OSError, ValueError, TypeError) as e: problems.append('internal evidence: '+str(e))
    for lang in LANGS: check_seller(out/n[lang], m, lang, internal, problems)
    eng = out/n['engineering']
    if not eng.is_dir(): problems.append('missing engineering folder: '+eng.name); return problems
    layout = engineering_layout(m)
    actual, _ = tree(eng)
    lookset_files = {name for name in actual if name.startswith(n['lookset']+'/')}
    for name in sorted(set(layout)-actual): problems.append(eng.name+': missing: '+name)
    for name in sorted(actual-set(layout)-lookset_files): problems.append(eng.name+': unexpected file: '+name)
    for name,spec in layout.items():
        file = eng/name
        if file.is_symlink() or (file.exists() and not file.is_file()):
            problems.append(eng.name+': not a regular file: '+name); continue
        if not file.is_file(): continue
        if spec[0] == 'copy' and sha256(file) != spec[2]: problems.append(eng.name+': hash mismatch: '+name)
        if spec[0] == 'manifest' and manifest_path and sha256(file) != sha256(manifest_path):
            problems.append(eng.name+': pack manifest copy differs: '+name)
        if spec[0] == 'version':
            run_copy = Path(m['run_dir'])/'c8'/version_manifest_name(m)
            if not run_copy.is_file() or sha256(file) != sha256(run_copy):
                problems.append(eng.name+': version manifest differs from RUN/c8 copy: '+name)
    check_version_manifest(out, m, problems)
    check_card(m, problems)
    lookset = eng/n['lookset']
    if lookset.is_dir(): check_lookset(lookset, m, problems)
    elif require_lookset: problems.append('Lookset package missing: '+str(lookset))
    return problems


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out-dir',required=True,help='folder holding the zh pack, en pack and engineering folder')
    p.add_argument('--manifest',required=True)
    p.add_argument('--require-lookset',action='store_true',help='D2 must exist inside the engineering folder')
    a=p.parse_args()
    try: problems=check(a.out_dir,load_manifest(a.manifest),a.manifest,a.require_lookset)
    except (OSError,ValueError,KeyError,TypeError) as e: problems=[str(e)]
    for problem in problems: print(problem)
    print(f'problems={len(problems)}')
    return int(bool(problems))


if __name__=='__main__': raise SystemExit(main())
