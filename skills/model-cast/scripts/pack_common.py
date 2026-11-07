"""Strict schema-2 manifest and deterministic V2 layout: zh pack, en pack, engineering folder."""
import json
import re
from pathlib import Path
from gen_request import sha256

IDS = [f'{i:02}' for i in range(1,13)]
# File names inside the AI zip: NN_<angle>.png (names used in the 2026-11-06 zip tests).
ANGLES = dict(zip(IDS, ['脸部正面','脸部45度','脸部侧面','全身正面','全身45度','全身侧面','全身背面',
                        '半身正面','半身45度','下半身正面','下半身45度','下半身背面']))
AI_README = '00_AI请先读这个.txt'
LANGS = ('zh','en')
# Per-language seller folders (index 0 = read only, 1 = upload, 2 = lifestyle) and file names.
SELLER = {
    'zh': dict(folders=['1_给你看（不要上传）','2_上传给AI','3_生活场景图（可直接用）'],
               how_to_use='使用说明.txt', card='角色识别卡.png', limits='原创性与使用边界.txt',
               zip='模特资料_上传给AI.zip'),
    'en': dict(folders=['1_Read_me (do not upload)','2_Upload_to_AI','3_Lifestyle'],
               how_to_use='How_to_use.txt', card='Model_card.png', limits='Originality_and_limits.txt',
               zip='{model}_model_pack.zip'),
}
ENGINEERING_MANIFESTS = '清单'
# Fixed timestamp so the zip is byte-reproducible from the same sources.
ZIP_DATE = (2026,1,1,0,0,0)


def keys(value, expected, where):
    if not isinstance(value, dict):
        raise ValueError(f'{where}: expected object')
    missing, extra = set(expected)-set(value), set(value)-set(expected)
    if missing or extra:
        raise ValueError(f'{where}: missing keys={sorted(missing)}, extra keys={sorted(extra)}')


def nonempty(value, where):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{where}: expected nonempty string')


def component(value, where):
    nonempty(value, where)
    if '/' in value or '\\' in value or value in ('.','..'):
        raise ValueError(where+' must be a filename component')


def names(m):
    """Derived output names; the blueprint naming is <name>_品牌模特资料包_V<major>.<minor>."""
    model, version = m['model_name'], m['version']
    zh = f'{model}_品牌模特资料包_{version}'
    return dict(zh=zh, en=f'{model}_Brand_Model_Pack_{version}_EN', engineering=f'{model}_{version}_工程资料',
                lookset=f'{zh}-model-reference', zip_root=f'模特资料_{m["name_zh"]}')


def load_manifest(path):
    path = Path(path).resolve()
    m = json.loads(path.read_text())
    keys(m, ['schema','model_name','name_zh','version','run_dir','originals','motion','texts','identity_card','diagram','lookset'], 'manifest')
    if type(m['schema']) is not int or m['schema'] != 2:
        raise ValueError('schema must be 2')
    component(m['model_name'],'model_name'); component(m['name_zh'],'name_zh')
    nonempty(m['version'],'version'); nonempty(m['run_dir'],'run_dir')
    if not re.fullmatch(r'V[2-9]\d*\.\d+', m['version']):
        raise ValueError('version must be V<major>.<minor> with major >= 2 (V1.x used the retired layout)')
    def resolve(value):
        nonempty(value,'source path')
        return str((path.parent / value).resolve())
    m['run_dir'] = resolve(m['run_dir'])
    def asset(a, where):
        keys(a,['path','sha256'],where)
        a['path'] = resolve(a['path'])
        if not isinstance(a['sha256'],str) or not re.fullmatch('[0-9a-f]{64}',a['sha256']):
            raise ValueError(where+': invalid sha256')
        if Path(a['path']).suffix.lower() != '.png':
            raise ValueError(where+': expected PNG')
    for group, expected in [('originals',['P3-2']+IDS),('motion',['walk','sit','smile'])]:
        keys(m[group],expected,group)
        for name,a in m[group].items(): asset(a,group+'.'+name)
    keys(m['identity_card'],LANGS,'identity_card')
    for lang in LANGS: asset(m['identity_card'][lang],'identity_card.'+lang)
    asset(m['diagram'],'diagram')
    t = m['texts']
    keys(t,['ai_readme','how_to_use','originality','boundary'],'texts')
    t['ai_readme'] = resolve(t['ai_readme'])
    for name in ('how_to_use','originality','boundary'):
        keys(t[name],LANGS,'texts.'+name)
        t[name] = {lang:resolve(t[name][lang]) for lang in LANGS}
    keys(m['lookset'],['confirmation_note','supplement_notes','locked','adjustable','styling_lock'],'lookset')
    d = m['lookset']
    nonempty(d['confirmation_note'],'lookset.confirmation_note')
    keys(d['supplement_notes'],IDS,'lookset.supplement_notes')
    for name,note in d['supplement_notes'].items(): nonempty(note,'supplement_notes.'+name)
    for name in ('locked','adjustable'):
        if not isinstance(d[name],list) or not d[name]: raise ValueError('lookset.'+name+': expected nonempty list')
        for value in d[name]: nonempty(value,'lookset.'+name)
    if len(d['locked']) != 3 or d['locked'][-1] != 'balanced regular build, natural waist, realistic leg length':
        raise ValueError('lookset.locked: two memory points and fixed body description required')
    if d['adjustable'] != ['hairstyle','makeup','expression','earrings and accessories'] or d['styling_lock'] != 'identity':
        raise ValueError('lookset adjustable/styling_lock differs from approved defaults')
    allowed = {a['sha256'] for a in m['originals'].values()}
    if allowed & display_hashes(m): raise ValueError('originals overlap with display/motion hashes')
    return m


def display_hashes(m):
    """Look-only and lifestyle images: never identity references, never inside the AI zip or D2."""
    return ({m['identity_card'][lang]['sha256'] for lang in LANGS} | {m['diagram']['sha256']}
            | {a['sha256'] for a in m['motion'].values()})


def joined_text(paths):
    """Seller text made of several sources, joined by one blank line; byte-for-byte reproducible."""
    return '\n\n'.join(Path(p).read_text(encoding='utf-8').rstrip('\n') for p in paths) + '\n'


def zip_members(m):
    """Member name -> (source path, expected sha256 or None for text). Order is the write order."""
    root = names(m)['zip_root']
    members = {f'{root}/{AI_README}': (m['texts']['ai_readme'], None)}
    for i in IDS:
        a = m['originals'][i]
        members[f'{root}/{i}_{ANGLES[i]}.png'] = (a['path'], a['sha256'])
    return members


def seller_layout(m, lang):
    """destination -> ('copy', source, sha256 or None, original id) | ('text', [sources]) | ('zip',)."""
    s = SELLER[lang]; f = s['folders']; t = m['texts']; c = m['identity_card'][lang]
    files = {
        f'{f[0]}/{s["how_to_use"]}': ('copy', t['how_to_use'][lang], None, None),
        f'{f[0]}/{s["card"]}': ('copy', c['path'], c['sha256'], None),
        f'{f[0]}/{s["limits"]}': ('text', [t['originality'][lang], t['boundary'][lang]]),
        f'{f[1]}/{s["zip"].format(model=m["model_name"])}': ('zip',),
    }
    for name,a in m['motion'].items():
        files[f'{f[2]}/{name}.png'] = ('copy', a['path'], a['sha256'], name)
    return files


def version_manifest_name(m):
    return f'version-manifest-{m["version"]}.json'


def engineering_layout(m):
    """Engineering folder (never delivered). The D2 sub-folder is written by export_lookset."""
    a = m['diagram']
    return {'shooting-guide.png': ('copy', a['path'], a['sha256'], None),
            f'{ENGINEERING_MANIFESTS}/pack-manifest-{m["version"]}.json': ('manifest',),
            f'{ENGINEERING_MANIFESTS}/{version_manifest_name(m)}': ('version',)}


SELLER_RUN_TEXTS = ('c7/originality.zh.md','c7/originality.en.md')
INTERNAL_SKILL_TEXTS = ('references/phase1-prompts.md','references/phase2-prompts.md')


def text_sources(m):
    t = m['texts']
    return [t['ai_readme']] + [t[k][lang] for k in ('how_to_use','originality','boundary') for lang in LANGS]


PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'


def image_assets(m):
    return ([(g+'.'+k,a) for g in ('originals','motion') for k,a in m[g].items()]
            + [('identity_card.'+lang,m['identity_card'][lang]) for lang in LANGS] + [('diagram',m['diagram'])])


def verify_sources(m):
    for where,a in image_assets(m):
        with open(a['path'],'rb') as stream:
            if stream.read(8) != PNG_SIGNATURE: raise ValueError(where+': not a PNG file: '+a['path'])
        try:
            from PIL import Image
            with Image.open(a['path']) as image:
                if image.format != 'PNG': raise ValueError(image.format)
                image.load()  # full decode: a PNG header followed by other bytes fails here
        except ImportError as e: raise ValueError('tool-blocked: Pillow unavailable') from e
        except Exception as e: raise ValueError(where+': not a PNG file (cannot decode): '+a['path']) from e
    for group in ('originals','motion'):
        for name,a in m[group].items():
            if sha256(a['path']) != a['sha256']: raise ValueError(group+'.'+name+': source hash mismatch')
    for where,a in [('identity_card.'+lang,m['identity_card'][lang]) for lang in LANGS]+[('diagram',m['diagram'])]:
        if sha256(a['path']) != a['sha256']: raise ValueError(where+': source hash mismatch')
    root = Path(m['run_dir']).resolve()
    allowed_run = {root/name for name in SELLER_RUN_TEXTS}
    internal = internal_hashes(m)
    for source in text_sources(m):
        src = Path(source).resolve()
        if not src.read_text(encoding='utf-8').strip(): raise ValueError(str(src)+': empty text')
        if root in src.parents and src not in allowed_run:
            raise ValueError('internal run file used as seller text: '+str(src))
        if sha256(src) in internal:
            raise ValueError('seller text matches internal evidence content: '+str(src))


def internal_hashes(m):
    """Content of every run file except declared seller assets is internal evidence.

    Matching by content (not by file name) means renamed copies are still caught.
    """
    root = Path(m['run_dir']).resolve()
    allowed_paths = {root/name for name in SELLER_RUN_TEXTS}
    allowed = {a['sha256'] for group in ('originals','motion') for a in m[group].values()}
    allowed |= display_hashes(m)
    allowed |= {sha256(p) for p in allowed_paths if p.is_file()}
    paths = {p for p in root.rglob('*') if p.is_file() and not p.is_symlink() and p not in allowed_paths} if root.is_dir() else set()
    for record in list(paths):
        if record.name in ('receipt.json','request.json'):
            data=json.loads(record.read_text())
            for key in ('prompt_path','prompt_sent_path'):
                if data.get(key): paths.add(Path(data[key]))
    skill = Path(__file__).resolve().parents[1]
    paths |= {skill/name for name in INTERNAL_SKILL_TEXTS}
    return {sha256(path) for path in paths if path.is_file()} - allowed
