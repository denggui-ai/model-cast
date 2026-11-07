import hashlib
import json
from pathlib import Path
import shutil
import sys

import pytest

from test_scripts import invoke, SCRIPTS

sys.path.insert(0,str(SCRIPTS))
import pack_common
from pack_common import load_manifest, names, seller_layout, SELLER
from build_pack import build
from check_pack import check
import export_lookset

EXAMPLE=SCRIPTS.parent/'references/pack-manifest.example.json'


@pytest.fixture
def manifest(tmp_path):
    raw=json.loads(EXAMPLE.read_text())
    m=load_manifest(EXAMPLE)
    raw['run_dir']=m['run_dir']=str(tmp_path/'run')
    # Absolute paths so the manifest can live anywhere.
    for group in ('originals','motion'):
        for k,a in m[group].items(): raw[group][k]['path']=a['path']
    for lang in ('zh','en'): raw['identity_card'][lang]['path']=m['identity_card'][lang]['path']
    raw['diagram']['path']=m['diagram']['path']
    raw['texts']=json.loads(json.dumps(m['texts']))
    path=tmp_path/'manifest.json';path.write_text(json.dumps(raw,ensure_ascii=False))
    return path,load_manifest(path)


UPLOAD_FILES = {'01': '01_脸部正面.png', '04': '04_全身正面.png',
                '06': '06_全身侧面.png', '07': '07_全身背面.png'}


def _upload(out,m,lang):
    return out/names(m)[lang]/SELLER[lang]['folders'][1]


def test_build_check_export_validate(manifest,tmp_path):
    path,m=manifest;out=tmp_path/'packs';n=names(m)
    result=invoke('build_pack.py','--manifest',path,'--out-dir',out)
    assert result.returncode==0,result.stderr
    assert {p.name for p in out.iterdir()}=={n['zh'],n['en'],n['engineering']}
    assert n['zh']=='Yuning_品牌模特资料包_V3.0' and n['en']=='Yuning_Brand_Model_Pack_V3.0_EN'
    assert invoke('check_pack.py','--manifest',path,'--out-dir',out).stdout=='problems=0\n'
    assert invoke('build_pack.py','--manifest',path,'--out-dir',out).returncode==2
    # Both languages upload the same four original PNGs, with no other files or directories.
    for lang in ('zh','en'):
        upload=_upload(out,m,lang)
        assert {p.name for p in upload.iterdir()}==set(UPLOAD_FILES.values())
        for i,name in UPLOAD_FILES.items():
            data=(upload/name).read_bytes()
            assert data==Path(m['originals'][i]['path']).read_bytes()
            assert hashlib.sha256(data).hexdigest()==m['originals'][i]['sha256']
            assert data==(_upload(out,m,'zh')/name).read_bytes()
    lookset=out/n['engineering']/n['lookset']
    result=invoke('export_lookset.py','--manifest',path,'--out',lookset)
    assert result.returncode==0,result.stdout+result.stderr
    c8=Path(m['run_dir'])/'c8'
    assert json.loads((c8/'lookset-validate-V3.0.json').read_text())
    spec=json.loads((c8/'lookset-spec-V3.0.json').read_text())
    assert len(spec['supplements'])==12 and spec['references']==[m['originals']['P3-2']['path']]
    assert not {a['path'] for a in m['motion'].values()} & {a['path'] for a in spec['supplements']}
    assert invoke('check_pack.py','--manifest',path,'--out-dir',out,'--require-lookset').stdout=='problems=0\n'
    assert not (SCRIPTS.parent/'vendor/lookset/__pycache__').exists()
    version=json.loads((c8/'version-manifest-V3.0.json').read_text())
    assert len(version['files'])==2*len(seller_layout(m,'zh'))+1
    assert version['upload_files']==[dict(filename=name,sha256=m['originals'][i]['sha256']) for i,name in UPLOAD_FILES.items()]
    assert 'zip_members' not in version
    for lang in ('zh','en'):
        rows=[r for r in version['files'] if r['package']==n[lang] and r['path'].startswith(SELLER[lang]['folders'][1]+'/')]
        assert {r['original_id'] for r in rows}==set(UPLOAD_FILES)
    eng=out/n['engineering']/'清单'
    assert (eng/'version-manifest-V3.0.json').read_bytes()==(c8/'version-manifest-V3.0.json').read_bytes()
    assert (eng/'pack-manifest-V3.0.json').read_bytes()==path.read_bytes()
    # evidence is version-named and never overwritten
    again=invoke('export_lookset.py','--manifest',path,'--out',tmp_path/'other')
    assert again.returncode==2 and 'already exists' in again.stderr


def test_old_versions_are_not_touched(manifest,tmp_path):
    path,m=manifest;c8=Path(m['run_dir'])/'c8';c8.mkdir(parents=True)
    old={name:f'old {name}' for name in ('version-manifest.json','lookset-spec.json','lookset-validate.json','version-manifest-V1.0.json',
                                      'version-manifest-V2.0.json','lookset-spec-V2.0.json','lookset-validate-V2.0.json')}
    for name,text in old.items(): (c8/name).write_text(text)
    old_packages=[]
    for key in ('zh','en','engineering'):
        package=tmp_path/'packs'/names(dict(m,version='V2.0'))[key]
        package.mkdir(parents=True);sentinel=package/'keep';sentinel.write_bytes(b'V2.0 original');old_packages.append(sentinel)
    build(m,tmp_path/'packs')
    assert export_lookset.export(m,tmp_path/'packs'/names(m)['engineering']/names(m)['lookset'])==0
    for name,text in old.items(): assert (c8/name).read_text()==text
    for sentinel in old_packages: assert sentinel.read_bytes()==b'V2.0 original'


def test_version_manifest_exists_refuses(manifest,tmp_path):
    _,m=manifest;c8=Path(m['run_dir'])/'c8';c8.mkdir(parents=True);(c8/'version-manifest-V3.0.json').write_text('{}')
    with pytest.raises(ValueError,match='never overwritten'): build(m,tmp_path/'packs')
    assert not (tmp_path/'packs').exists()


def test_copy_hash_failure_cleans_only_new_pack(manifest,tmp_path,monkeypatch):
    _,m=manifest;(tmp_path/'packs').mkdir();(tmp_path/'packs'/'keep').write_text('x')
    original=shutil.copyfile
    def corrupt(src,dst):
        original(src,dst);Path(dst).write_bytes(b'corruption')
    monkeypatch.setattr(shutil,'copyfile',corrupt)
    with pytest.raises(OSError,match='copied hash mismatch'): build(m,tmp_path/'packs')
    assert [p.name for p in (tmp_path/'packs').iterdir()]==['keep']
    assert not (Path(m['run_dir'])/'c8/version-manifest-V3.0.json').exists()


CASES=['folder','card_swap','limits_text','internal','engineering_extra','lookset','missing_en']


@pytest.mark.parametrize('case',CASES)
def test_check_failures(manifest,tmp_path,case,monkeypatch):
    path,m=manifest;out=tmp_path/'packs';build(m,out);n=names(m)
    zh=out/n['zh']
    if case=='folder': shutil.rmtree(zh/SELLER['zh']['folders'][2])
    if case=='card_swap': shutil.copyfile(m['identity_card']['en']['path'],zh/SELLER['zh']['folders'][0]/SELLER['zh']['card'])
    if case=='limits_text': (zh/SELLER['zh']['folders'][0]/SELLER['zh']['limits']).write_text('edited')
    if case=='internal': (zh/'receipt.json').write_text('{}')
    if case=='engineering_extra': (out/n['engineering']/'receipt.json').write_text('{}')
    if case=='lookset':
        bad=out/n['engineering']/n['lookset'];bad.mkdir();shutil.copyfile(m['motion']['walk']['path'],bad/'bad.png')
    if case=='missing_en': shutil.rmtree(out/n['en'])
    problems=check(out,m,path)
    assert problems
    result=invoke('check_pack.py','--manifest',path,'--out-dir',out)
    assert result.returncode==1 and 'problems=0\n' not in result.stdout


@pytest.mark.parametrize('lang',['zh','en'])
@pytest.mark.parametrize('case',['wrong_original','missing','extra_original','extra_zip','extra_readme','card','diagram','lifestyle','nested'])
def test_upload_rejects_wrong_or_extra_files(manifest,tmp_path,lang,case):
    path,m=manifest;out=tmp_path/'packs';build(m,out,path);upload=_upload(out,m,lang)
    target=upload/UPLOAD_FILES['04']
    expected='hash mismatch'
    if case=='wrong_original': shutil.copyfile(m['originals']['02']['path'],target)
    elif case=='missing': target.unlink();expected='missing:'
    elif case=='extra_original': shutil.copyfile(m['originals']['02']['path'],upload/'02_脸部45度.png');expected='unexpected/internal file'
    elif case=='extra_zip': (upload/'model.zip').write_bytes(b'PK');expected='unexpected/internal file'
    elif case=='extra_readme': (upload/'00_AI请先读这个.txt').write_text('retired instructions');expected='unexpected/internal file'
    elif case=='nested': (upload/'nested').mkdir();expected='unexpected directory'
    else:
        source={'card':m['identity_card'][lang], 'diagram':m['diagram'], 'lifestyle':m['motion']['walk']}[case]
        shutil.copyfile(source['path'],target);expected='display/lifestyle image in upload folder'
    problems=check(out,m,path)
    assert any(expected in p and names(m)[lang] in p for p in problems),problems
    result=invoke('check_pack.py','--manifest',path,'--out-dir',out)
    assert result.returncode==1 and 'problems=0\n' not in result.stdout


@pytest.mark.parametrize('mode',['extra','missing','nested','schema1','v1','v2','overlap','card_lang'])
def test_manifest_rejects(manifest,tmp_path,mode):
    path,m=manifest;raw=json.loads(path.read_text())
    if mode=='extra': raw['surprise']=1
    if mode=='missing': del raw['version']
    if mode=='nested': raw['originals']['01']['unexpected']=True
    if mode=='schema1': raw['schema']=1
    if mode=='v1': raw['version']='V1.0'
    if mode=='v2': raw['version']='V2.0'
    if mode=='overlap': raw['diagram']=dict(raw['originals']['01'])
    if mode=='card_lang': del raw['identity_card']['en']
    path.write_text(json.dumps(raw,ensure_ascii=False))
    result=invoke('build_pack.py','--manifest',path,'--out-dir',tmp_path/'packs')
    assert result.returncode==2,result.stderr
    assert not (tmp_path/'packs').exists()


@pytest.mark.parametrize('version',['V3.0','V9.9','V10.0','V12.1','V100.0'])
def test_manifest_accepts_supported_major_versions(manifest,version):
    path,_=manifest;raw=json.loads(path.read_text());raw['version']=version
    path.write_text(json.dumps(raw,ensure_ascii=False))
    assert load_manifest(path)['version']==version


@pytest.mark.parametrize('version',['V1.0','V2.0','V2.9'])
def test_manifest_rejects_retired_major_versions(manifest,version):
    path,_=manifest;raw=json.loads(path.read_text());raw['version']=version
    path.write_text(json.dumps(raw,ensure_ascii=False))
    with pytest.raises(ValueError,match='major >= 3'):
        load_manifest(path)


def test_internal_manifest_cannot_be_written_inside_package(manifest,tmp_path):
    _,m=manifest
    m['run_dir']=str(tmp_path/'packs'/names(m)['zh'])
    with pytest.raises(ValueError,match='outside seller'): build(m,tmp_path/'packs')
    assert not (tmp_path/'packs').exists()


# --- F1 regressions (2026-11-06 reverse audit), kept for the V3 layout ---

def _run_internal(m,name,text):
    path=Path(m['run_dir'])/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text);return path


def test_f1_internal_run_file_as_seller_text_is_rejected(manifest,tmp_path):
    path,m=manifest
    spec=_run_internal(m,'c8/lookset-spec.json','{"internal_note":"DO NOT SHIP"}')
    raw=json.loads(path.read_text())
    raw['texts']['how_to_use']['zh']=str(spec)
    path.write_text(json.dumps(raw,ensure_ascii=False))
    result=invoke('build_pack.py','--manifest',path,'--out-dir',tmp_path/'packs')
    assert result.returncode!=0 and 'lookset-spec.json' in result.stderr+result.stdout
    assert not (tmp_path/'packs').exists()


def test_f1_renamed_internal_content_and_later_edit_are_caught(manifest,tmp_path):
    path,m=manifest
    _run_internal(m,'c6/selfcheck.md','INTERNAL POC DRAFT')
    outside=tmp_path/'innocent-name.txt';outside.write_text('INTERNAL POC DRAFT')
    raw=json.loads(path.read_text());raw['texts']['how_to_use']['zh']=str(outside);path.write_text(json.dumps(raw,ensure_ascii=False))
    result=invoke('build_pack.py','--manifest',path,'--out-dir',tmp_path/'packs')
    assert result.returncode!=0
    # A clean build that is edited afterwards must also fail, including renamed evidence in an upload image.
    m=load_manifest(EXAMPLE);m['run_dir']=str(tmp_path/'run');out=tmp_path/'packs2';build(m,out)
    en=out/names(m)['en']/SELLER['en']['folders'][0]/SELLER['en']['how_to_use'];en.write_text('INTERNAL POC DRAFT')
    assert any('internal' in p for p in check(out,m))
    en.write_text(Path(m['texts']['how_to_use']['en']).read_text())
    for lang in ('zh','en'):
        target=_upload(out,m,lang)/UPLOAD_FILES['01'];target.write_text('INTERNAL POC DRAFT')
        assert any('internal evidence content in package' in p and SELLER[lang]['folders'][1] in p for p in check(out,m))
        target.write_bytes(Path(m['originals']['01']['path']).read_bytes())


def test_f1_originality_from_run_is_allowed(manifest,tmp_path):
    path,m=manifest
    raw=json.loads(path.read_text())
    for lang in ('zh','en'):
        raw['texts']['originality'][lang]=str(_run_internal(m,f'c7/originality.{lang}.md',f'原创性说明 {lang}'))
    _run_internal(m,'c6/selfcheck.md','自检')
    path.write_text(json.dumps(raw,ensure_ascii=False))
    assert invoke('build_pack.py','--manifest',path,'--out-dir',tmp_path/'packs').returncode==0
    assert invoke('check_pack.py','--manifest',path,'--out-dir',tmp_path/'packs').stdout=='problems=0\n'
    limits=(tmp_path/'packs'/names(m)['zh']/SELLER['zh']['folders'][0]/SELLER['zh']['limits']).read_text()
    assert limits.startswith('原创性说明 zh\n\n')


def test_real_templates_are_complete():
    """Seller instructions use direct photos; no retired AI instructions are shipped."""
    t=SCRIPTS.parent/'references/pack-templates'
    assert not (t/'ai-readme.zh.txt').exists()
    zh=(t/'how-to-use.zh.txt').read_text();en=(t/'how-to-use.en.txt').read_text()
    assert '4 张照片' in zh and '测试过 4 次' in zh and '尚待店主确认' in zh and '只想换某一件' in zh and '压缩包' not in zh
    assert '4 photos' in en and 'four times' in en and 'zip file' not in en
    for name in ('how-to-use.zh.txt','how-to-use.en.txt','boundary.zh.txt','boundary.en.txt'):
        text=(t/name).read_text()
        assert '05_上半身' not in text and '提示词.txt' not in text and '01_开始换装' not in text
    assert not (t/'prompts').exists()


@pytest.mark.parametrize('mode',['file','metadata'])
def test_vendor_tampering_exit_two(manifest,tmp_path,mode):
    # Exercise CLI against an isolated skill copy, never change committed vendor.
    skill=tmp_path/'skill';shutil.copytree(SCRIPTS,skill/'scripts');shutil.copytree(export_lookset.VENDOR,skill/'vendor/lookset')
    if mode=='file':
        with (skill/'vendor/lookset/model_reference.py').open('a') as f: f.write('\n# modified\n')
    else:
        p=skill/'vendor/lookset/VENDOR.json';d=json.loads(p.read_text());d['files'][0]['sha256']='0'*64;p.write_text(json.dumps(d))
    import subprocess,os
    result=subprocess.run([sys.executable,'-B',str(skill/'scripts/export_lookset.py'),'--manifest',str(manifest[0]),'--out',str(tmp_path/'out')],env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True)
    assert result.returncode==2,result.stderr
    assert 'actual=' in result.stderr and not (tmp_path/'out').exists()


def test_vendor_pinned_bytes():
    locks=dict(export_lookset.LOCKS,LICENSE='c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4')
    for name,digest in locks.items(): assert hashlib.sha256((export_lookset.VENDOR/name).read_bytes()).hexdigest()==digest


def test_records_aggregate_without_judgment(tmp_path):
    for name,text in [('c4/selection.md','Owner 原话'),('c6/selfcheck.md','自检原文 C6'),('n2/selfcheck.md','自检原文 N2'),('p3/prompt.txt','固定提示词原文')]:
        path=tmp_path/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
    receipt=dict(id='p3-2',purpose='candidate',prompt_path=str(tmp_path/'p3/prompt.txt'),prompt_sha256='a'*64,refs=[],status='ok',codex_cli_version='codex-cli 0.161.0',outputs=[])
    (tmp_path/'p3/receipt.json').write_text(json.dumps(receipt))
    result=invoke('build_records.py','--run-dir',tmp_path,'--selection-ids','p3-2')
    assert result.returncode==0,result.stderr
    text=(tmp_path/'c7/records.md').read_text()
    assert text.count('\n# ')==3
    for value in ['Owner 原话','自检原文 C6','自检原文 N2','固定提示词原文','p3-2','a'*64]: assert value in text



def test_f3_records_separate_formal_selection_from_history(tmp_path):
    def receipt(rid,purpose,status='ok',prompt='p3/prompt.txt'):
        d=tmp_path/rid;d.mkdir(parents=True,exist_ok=True);out=d/(rid+'.png');out.write_bytes(rid.encode())
        r=dict(id=rid,purpose=purpose,prompt_path=str(tmp_path/prompt),prompt_sha256='b'*64,refs=[],status=status,
               codex_cli_version='codex-cli 0.161.0',output_path=str(out) if status=='ok' else None,
               outputs=[dict(output_path=str(out))])
        (d/'receipt.json').write_text(json.dumps(r))
    for name,text in [('c4/selection.md','Owner 原话：选 P3-2'),('c6/selfcheck.md','C6'),('n2/selfcheck.md','N2'),
                      ('p3/prompt.txt','固定选人提示词'),('old/prompt.txt','OLD-HISTORY-PROMPT')]:
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
    for i in range(1,6): receipt(f'p3-{i}','candidate')
    receipt('c2-r1-A-1','candidate','size_fail','old/prompt.txt');receipt('e1-1','candidate','ok','old/prompt.txt')
    receipt('c4-01-1','face01');receipt('c6-02-1','face_angle')
    result=invoke('build_records.py','--run-dir',tmp_path,'--selection-ids','p3-1,p3-2,p3-3,p3-4,p3-5')
    assert result.returncode==0,result.stderr
    text=(tmp_path/'c7/records.md').read_text()
    formal=text.split('\n# 2.')[0]
    assert formal.count('固定选人提示词')==1 and all(f'p3-{i}' in formal for i in range(1,6))
    assert 'OLD-HISTORY-PROMPT' not in text and 'Owner 原话：选 P3-2' in formal
    assert '历史' in formal and 'c2-r1-A-1' in formal and 'size_fail' in formal
    section2=text.split('\n# 2.')[1].split('\n# 3.')[0]
    assert 'c4-01-1' in section2 and 'c6-02-1' in section2 and 'e1-1' not in section2
    section4=text.split('\n# 4.')[1]
    assert 'c2-r1-A-1.png' not in section4 and 'p3-2.png' in section4 and 'c6-02-1.png' in section4
    bad=invoke('build_records.py','--run-dir',tmp_path,'--selection-ids','p3-1,p3-9')
    assert bad.returncode==2


# --- F2 regression: CJK glyphs and long labels (2026-11-06 reverse audit) ---

LONG_LABEL='02 脸部 45° / Face 45°\\n记忆点：圆润饱满的面颊配小而圆的下巴；平缓弧眉配笑起来微弯、眼尾略下垂的杏眼 / 身份未验证'


def test_f2_sheet_uses_cjk_font_and_wraps_long_labels(tmp_path):
    from PIL import Image
    src=SCRIPTS.parents[2]/'tests/fixtures/phase2/01.png'
    out=tmp_path/'sheet.png'
    items=[]
    for i in range(3): items += ['--item',f'{src}={LONG_LABEL}']
    result=invoke('compose_sheet.py','--out',out,'--cols','2','--cell','300x200',*items)
    assert result.returncode==0,result.stderr
    record=json.loads((tmp_path/'sheet.png.sheet.json').read_text())
    assert record['font'] and Path(record['font']).is_file()
    from PIL import ImageFont
    font=ImageFont.truetype(record['font'],20)
    assert bytes(font.getmask('圆'))!=bytes(font.getmask('眉'))
    with Image.open(out) as image:
        # 2 rows; label band must be taller than the old fixed 40px to hold wrapped lines
        assert image.size[0]==600 and image.size[1]>2*(200+40)
    assert invoke('check_run.py','--run-dir',tmp_path).returncode==0


def test_f2_font_without_cjk_is_an_error(tmp_path):
    latin='/System/Library/Fonts/Supplemental/Arial.ttf'
    if not Path(latin).is_file(): pytest.skip('host has no Latin-only reference font')
    src=SCRIPTS.parents[2]/'tests/fixtures/phase2/01.png'
    result=invoke('compose_sheet.py','--out',tmp_path/'s.png','--cols','1','--cell','300x200','--font',latin,'--item',f'{src}=圆润')
    assert result.returncode==2 and 'tool-blocked' in result.stderr
    assert not (tmp_path/'s.png').exists()


def test_f3_duplicate_receipt_id_is_an_error(tmp_path):
    for name in ('c4/selection.md','c6/selfcheck.md','n2/selfcheck.md','p/prompt.txt'):
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('x')
    for d in ('a','b'):
        p=tmp_path/d/'receipt.json';p.parent.mkdir();p.write_text(json.dumps(dict(id='p3-1',purpose='candidate',prompt_path=str(tmp_path/'p/prompt.txt'),status='ok',outputs=[])))
    assert invoke('build_records.py','--run-dir',tmp_path,'--selection-ids','p3-1').returncode==2


def test_f2_degree_sign_stays_with_number():
    from PIL import Image, ImageDraw, ImageFont
    import compose_sheet
    font,_=compose_sheet.pick_font(ImageFont,['05 全身 45° / Full body 45°'])
    draw=ImageDraw.Draw(Image.new('RGB',(1,1)))
    width=draw.textlength('05 全身 45° / Full body 45',font=font)
    lines=compose_sheet.wrap(draw,font,'05 全身 45° / Full body 45°',width)
    assert not any(line.startswith('°') for line in lines), lines
    assert ''.join(lines).replace(' ','')=='05全身45°/Fullbody45°'



# --- T14: formal model card is laid out from originals only ---

def _card_spec(tmp_path,detail_src=None):
    fx=SCRIPTS.parents[2]/'tests/fixtures/phase2'
    details=[]
    for i,box in enumerate(('0,0,2,2','1,1,3,3')):
        out=tmp_path/f'd{i}.png'
        assert invoke('crop.py','--src',detail_src or fx/'01.png','--box',box,'--out',out).returncode==0
        details.append(dict(path=str(out),title=f'记忆点 {i+1}',label='圆润面颊' if i==0 else '平缓弧眉'))
    spec=dict(schema=2,name='语宁 Yuning',card_type='角色识别卡',tags=['原创成年女模特','资料包 V2.0','原图排版'],
              face=dict(path=str(fx/'01.png'),label='01 正脸'),
              profile=dict(heading='身份档案',rows=[['名字','语宁 Yuning'],['体型','自然（约 M 码），比例真实。']],note='设计设定，不是真人资料。'),
              recognize=dict(heading='怎么认出她',details=details,tip='先看这两处还在不在。'),
              turnaround=dict(heading='转身图',items=[dict(path=str(fx/f'{i}.png'),label=f'{i} 全身 45°') for i in ('04','05','06','07')]),
              positioning=dict(heading='适合的商品和顾客',rows=[['产品线','白色短款羽绒马甲'],['穿着者','25–35 岁城市女性']]),
              reasons=dict(heading='为什么定她',label='选角说明（选人时只记了一句理由，这段是事后补写的）',
                           points=[dict(title='客群',text='白色短款连帽羽绒马甲，穿着者 25–35 岁城市女性，S–L 码（店主已确认）。衣服休闲里带一点精致，所以选看着亲切、日常的模特，不选高冷大片脸。'),
                                   dict(title='脸型和气质',text='面颊圆润、下巴小而圆，线条柔和；我们的判断是，这和马甲蓬松的绗缝、圆润的帽口是同一种感觉。年轻甜美，妆容表情不夸张。'),
                                   dict(title='发型、妆容、表情',text='低马尾收在脑后，脸、肩线和领口都露出来，不挡帽口和领部；淡妆、暖唇色、自然微笑。'),
                                   dict(title='基础搭配',text='米白针织长袖、深灰直筒牛仔裤、米白平底鞋，都是素色；换装时当一块干净的底，不和你的商品抢。'),
                                   dict(title='认得出、定得住',text='两处记忆点在能看清脸的角度里都保持住了，适合固定成同一个人反复使用。')],
                           note='原图都经店主逐张确认。'),
              rules=dict(heading='使用规则',fixed_heading='不能变',fixed=['两处记忆点','脸型和五官比例'],
                         variable_heading='可以变',variable=['衣服','发型'],notes=['侧面背面未验证']),footer='原创性和使用边界见同一文件夹。')
    path=tmp_path/'spec.json';path.write_text(json.dumps(spec,ensure_ascii=False));return path


@pytest.mark.parametrize('theme,note_count',[(None,1),('ink',2),('cream',3)])
def test_make_card_records_sources_and_passes_check_run(tmp_path,theme,note_count):
    from PIL import Image, ImageColor
    import make_card
    spec=_card_spec(tmp_path);out=tmp_path/'card.png'
    raw=json.loads(spec.read_text());raw['rules']['notes']*=note_count
    spec.write_text(json.dumps(raw,ensure_ascii=False))
    result=invoke('make_card.py','--spec',spec,'--out',out,*(['--theme',theme] if theme else []))
    assert result.returncode==0,result.stderr
    with Image.open(out) as card:
        assert card.getpixel((0,0))==ImageColor.getrgb(make_card.THEMES[theme or 'cream']['paper'])
    record=json.loads((tmp_path/'card.png.sheet.json').read_text())
    assert len(record['sources'])==7 and record['card_spec']['sha256']==hashlib.sha256(spec.read_bytes()).hexdigest()
    assert set(record)=={'sources','output_sha256','font','card_spec'}
    raw=json.loads(spec.read_text())
    assert [s['label'] for s in record['sources']]==[raw['face']['label']]+[
        f"{d['title']}：{d['label']}" for d in raw['recognize']['details']]+[t['label'] for t in raw['turnaround']['items']]
    assert invoke('check_run.py','--run-dir',tmp_path).returncode==0
    assert invoke('make_card.py','--spec',spec,'--out',out).returncode==2  # never overwrite


def test_make_card_rejects_close_up_not_cropped_from_face(tmp_path):
    spec=_card_spec(tmp_path,detail_src=SCRIPTS.parents[2]/'tests/fixtures/phase2/02.png')
    result=invoke('make_card.py','--spec',spec,'--out',tmp_path/'card.png')
    assert result.returncode==2 and 'not a crop.py output' in result.stderr
    assert not (tmp_path/'card.png').exists()


@pytest.mark.parametrize('target',[
    (),('face',),('profile',),('recognize',),('recognize','details',0),
    ('turnaround',),('turnaround','items',0),('positioning',),('reasons',),('reasons','points',0),('rules',),
])
@pytest.mark.parametrize('change',['missing','extra'])
def test_make_card_rejects_wrong_keys_at_every_level(tmp_path,target,change):
    spec=_card_spec(tmp_path);raw=json.loads(spec.read_text());obj=raw
    for key in target: obj=obj[key]
    if change=='missing': del obj[next(iter(obj))]
    else: obj['unexpected']='must not be ignored'
    spec.write_text(json.dumps(raw,ensure_ascii=False))
    result=invoke('make_card.py','--spec',spec,'--out',tmp_path/'card.png')
    assert result.returncode==2 and 'keys' in result.stderr
    assert not (tmp_path/'card.png').exists() and not (tmp_path/'card.png.sheet.json').exists()


@pytest.mark.parametrize('case',[
    'schema1','tags','details','turnaround','profile_rows','positioning_rows','text_type',
    'reason_title','reason_label','reason_note','points_short','points_long','points_strings',
    'notes_empty','notes_long','notes_type',
])
def test_make_card_rejects_old_schema_and_malformed_structure(tmp_path,case):
    spec=_card_spec(tmp_path);raw=json.loads(spec.read_text())
    if case=='schema1': raw['schema']=1
    if case=='tags': raw['tags'].pop()
    if case=='details': raw['recognize']['details'].pop()
    if case=='turnaround': raw['turnaround']['items'].pop()
    if case=='profile_rows': raw['profile']['rows'][0]=['key','value','extra']
    if case=='positioning_rows': raw['positioning']['rows'][0]='not a pair'
    if case=='text_type': raw['reasons']['points'][0]['text']=None
    if case=='reason_title': raw['reasons']['points'][0]['title']=' '
    if case=='reason_label': raw['reasons']['label']=None
    if case=='reason_note': raw['reasons']['note']=[]
    if case=='points_short': raw['reasons']['points'].pop()
    if case=='points_long': raw['reasons']['points']*=2
    if case=='points_strings': raw['reasons']['points']=['旧版文字']*5
    if case=='notes_empty': raw['rules']['notes']=[]
    if case=='notes_long': raw['rules']['notes']*=4
    if case=='notes_type': raw['rules']['notes']=['正常提示',None]
    spec.write_text(json.dumps(raw,ensure_ascii=False))
    result=invoke('make_card.py','--spec',spec,'--out',tmp_path/'card.png')
    assert result.returncode==2 and 'Traceback' not in result.stderr
    assert not (tmp_path/'card.png').exists()


@pytest.mark.parametrize('legacy',['old_shape','records','records_heading'])
def test_make_card_rejects_legacy_reasons(tmp_path,legacy):
    spec=_card_spec(tmp_path);raw=json.loads(spec.read_text())
    old=dict(heading='为什么定她',points=['年轻甜美'],records_heading='店主确认记录（原话）',
             records=[dict(date='2026-11-05',what='确认穿着者和尺码',quote='对的')])
    if legacy=='old_shape': raw['reasons']=old
    else: raw['reasons'][legacy]=old[legacy]
    spec.write_text(json.dumps(raw,ensure_ascii=False))
    result=invoke('make_card.py','--spec',spec,'--out',tmp_path/'card.png')
    assert result.returncode==2 and 'reasons keys' in result.stderr
    assert not (tmp_path/'card.png').exists() and not (tmp_path/'card.png.sheet.json').exists()


def test_make_card_rejects_close_up_changed_after_crop(tmp_path):
    from PIL import Image
    spec=_card_spec(tmp_path)
    detail=Path(json.loads(spec.read_text())['recognize']['details'][0]['path'])
    Image.new('RGB',(2,2),'red').save(detail)
    result=invoke('make_card.py','--spec',spec,'--out',tmp_path/'card.png')
    assert result.returncode==2 and 'changed after cropping' in result.stderr
    assert not (tmp_path/'card.png').exists()


@pytest.mark.parametrize('theme',['cream','ink'])
def test_make_card_theme_contrast(theme):
    import make_card
    colors=make_card.THEMES[theme]
    for surface in ('paper','panel','tint'):
        assert make_card.contrast_ratio(colors['ink'],colors[surface])>=7
        assert make_card.contrast_ratio(colors['muted'],colors[surface])>=4.5
        assert make_card.contrast_ratio(colors['accent'],colors[surface])>=7
    assert make_card.contrast_ratio(colors['panel'],colors['accent'])>=7


def test_make_card_draws_every_spec_text_verbatim(tmp_path,monkeypatch):
    from collections import Counter
    from PIL import ImageDraw
    import make_card
    path=_card_spec(tmp_path);spec=make_card.load_spec(path);drawn=[]
    def literal_text(value):
        if isinstance(value,str): return [value]
        if isinstance(value,list): return [s for child in value for s in literal_text(child)]
        if isinstance(value,dict): return [s for key,child in value.items() if key!='path' for s in literal_text(child)]
        return []
    expected=literal_text(json.loads(path.read_text()))
    original=ImageDraw.ImageDraw.text
    def record_text(self,xy,text,*args,**kwargs):
        drawn.append(text)
        return original(self,xy,text,*args,**kwargs)
    monkeypatch.setattr(ImageDraw.ImageDraw,'text',record_text)
    make_card.render(spec,tmp_path/'card.png')
    def chars(parts): return Counter(ch for part in parts for ch in part if not ch.isspace())
    # Only section numbers, face/detail badges and the five point numbers are added.
    # badges 1/2 only on the close-ups; the face has no boxes (Owner 2026-11-06)
    assert chars(drawn)==chars(expected+['010203040506','12','12345'])


@pytest.mark.parametrize('text,first_line', [
    ('圆润饱满的面颊，配小而圆的下巴。', '圆润饱满的面颊'),
    ('体型：自然（约 M 码），比例真实。', '体型：自然（约 M 码'),
    ('店主确认“全部认可”；保留原图。', '店主确认“全部认可'),
    ('05 全身 45° / Full body 45°\n\n记忆点：杏眼、圆下巴。', '05 全身 45'),
])
def test_make_card_wrap_keeps_punctuation_with_text(text,first_line):
    from PIL import Image, ImageDraw, ImageFont
    import compose_sheet
    import make_card
    font,_=compose_sheet.pick_font(ImageFont,[text])
    draw=ImageDraw.Draw(Image.new('RGB',(1,1)))
    width=draw.textlength(first_line,font=font)
    lines=make_card.wrap(draw,font,text,width)
    assert all(not line or line[0] not in '，。、；：！？）》」』】”’°' for line in lines), lines
    assert all(not line or line[-1] not in '（《「『【“‘' for line in lines), lines
    assert all(draw.textlength(line,font=font)<=width for line in lines)
    assert ''.join(''.join(lines).split())==''.join(text.split())
    assert lines.count('')==text.count('\n\n')


@pytest.mark.parametrize('text,first_line,last_line', [
    ('不能变：两处记忆点、脸型和五官比例', '不能变：两处记忆点、脸型和五官比', '比例'),
    ('肤色（原图）：白皙、偏暖的自然肤色', '肤色（原图）：白皙、偏暖的自然肤', '肤色'),
    ('看换装结果时，先看这两处还在不在。', '看换装结果时，先看这两处还在不', '不在。'),
    ('店主确认“对的”', '店主确认“对', '“对的”'),
])
def test_make_card_wrap_avoids_lone_chinese_paragraph_end(text,first_line,last_line):
    from PIL import Image, ImageDraw, ImageFont
    import compose_sheet
    import make_card
    font,_=compose_sheet.pick_font(ImageFont,[text, '语宁'])
    draw=ImageDraw.Draw(Image.new('RGB',(1,1)))
    width=draw.textlength(first_line,font=font)
    # Explicit one-character paragraphs must not borrow across paragraph breaks.
    label='语\n\n'+text+'\n\n宁'
    lines=make_card.wrap(draw,font,label,width)
    assert lines[:2]==['语', ''] and lines[-2:]==['', '宁']
    assert lines[-3]==last_line, lines
    assert all(draw.textlength(line,font=font)<=width for line in lines)
    assert all(not line or line[0] not in make_card.NO_LINE_START for line in lines)
    assert all(not line or line[-1] not in make_card.NO_LINE_END for line in lines)
    assert ''.join(lines)==label.replace('\n', '')


# --- T14 review (deepseek_code batch 2): symlink in engineering folder ---

def test_engineering_symlink_is_a_problem(manifest,tmp_path):
    path,m=manifest;out=tmp_path/'packs';build(m,out)
    guide=out/names(m)['engineering']/'shooting-guide.png';guide.unlink();(tmp_path/'d').mkdir();guide.symlink_to(tmp_path/'d')
    assert any('shooting-guide.png' in p for p in check(out,m,path))


@pytest.mark.parametrize('case',['hash','missing','extra','duplicate'])
def test_version_manifest_upload_files_must_match(manifest,tmp_path,case):
    path,m=manifest;out=tmp_path/'packs';build(m,out,path)
    version=Path(m['run_dir'])/'c8/version-manifest-V3.0.json'
    data=json.loads(version.read_text());rows=data['upload_files']
    if case=='hash': rows[0]['sha256']='0'*64
    elif case=='missing': rows.pop()
    elif case=='extra': rows.append(dict(filename='02_脸部45度.png',sha256=m['originals']['02']['sha256']))
    else: rows.append(dict(rows[0]))
    version.write_text(json.dumps(data,ensure_ascii=False))
    shutil.copyfile(version,out/names(m)['engineering']/'清单'/version.name)
    assert any('version manifest upload files are stale' in p for p in check(out,m,path))


def test_make_card_orphan_fix_keeps_space_before_latin_word():
    # T14b review: pulling an English word down next to a lone CJK char dropped the space ('M) 脸' -> 'M)脸').
    from PIL import Image, ImageDraw, ImageFont
    import compose_sheet, make_card
    text='the 脸 memory 脸 下巴 下巴 points, M) 脸'
    font,_=compose_sheet.pick_font(ImageFont,[text])
    draw=ImageDraw.Draw(Image.new('RGB',(1,1)))
    lines=make_card.wrap(draw,font,text,386)
    assert not any('M)脸' in line for line in lines), lines


# --- Final review (2026-11-06): codex-review + final-reviewer findings, each reproduced first ---

def _built(manifest,tmp_path,lookset=False):
    path,m=manifest;out=tmp_path/'packs';build(m,out,path)
    if lookset: assert export_lookset.export(m,out/names(m)['engineering']/names(m)['lookset'])==0
    return path,m,out


@pytest.mark.parametrize('lang',['zh','en'])
def test_upload_symlink_is_a_problem(manifest,tmp_path,lang):
    path,m,out=_built(manifest,tmp_path)
    target=_upload(out,m,lang)/UPLOAD_FILES['04'];target.unlink();target.symlink_to(m['originals']['04']['path'])
    assert any('symlink' in p and SELLER[lang]['folders'][1] in p for p in check(out,m,path))


def test_lookset_extra_or_missing_files_are_problems(manifest,tmp_path):
    path,m,out=_built(manifest,tmp_path,lookset=True)
    d2=out/names(m)['engineering']/names(m)['lookset']
    assert check(out,m,path,True)==[]
    shutil.copyfile(m['motion']['walk']['path'],d2/'walk.gif');(d2/'selfcheck.md').write_text('internal')
    problems=check(out,m,path,True)
    assert any('walk.gif' in p for p in problems) and any('selfcheck.md' in p for p in problems)
    (d2/'walk.gif').unlink();(d2/'selfcheck.md').unlink();(d2/'supplements/12.png').unlink()
    assert any('supplements/12.png' in p for p in check(out,m,path,True))


def test_non_png_declared_as_original_is_rejected(manifest,tmp_path):
    path,m=manifest
    fake=tmp_path/'run/records.png';fake.parent.mkdir(parents=True);fake.write_text('INTERNAL RECORDS')
    raw=json.loads(path.read_text());raw['originals']['01']=dict(path=str(fake),sha256=hashlib.sha256(fake.read_bytes()).hexdigest())
    path.write_text(json.dumps(raw,ensure_ascii=False))
    result=invoke('build_pack.py','--manifest',path,'--out-dir',tmp_path/'packs')
    assert result.returncode!=0 and 'not a PNG' in result.stderr+result.stdout


def test_partial_version_manifest_is_removed_on_failure(manifest,tmp_path,monkeypatch):
    _,m=manifest;version=Path(m['run_dir'])/'c8/version-manifest-V3.0.json'
    real_open=Path.open
    class Failing:
        # Simulates a real write failure (e.g. RLIMIT_FSIZE) after the file was created.
        def __init__(self,stream): self.stream=stream
        def __enter__(self): return self
        def __exit__(self,*exc): self.stream.close()
        def write(self,text): self.stream.write(text[:10]);self.stream.flush();raise OSError('disk full')
    def failing(self,mode='r',*a,**k):
        stream=real_open(self,mode,*a,**k)
        return Failing(stream) if self==version and 'x' in mode else stream
    monkeypatch.setattr(Path,'open',failing)
    with pytest.raises(OSError,match='disk full'): build(m,tmp_path/'packs')
    monkeypatch.undo()
    assert not version.exists()
    build(m,tmp_path/'packs2')


def test_stale_version_manifest_is_a_problem(manifest,tmp_path):
    path,m,out=_built(manifest,tmp_path)
    how=out/names(m)['zh']/SELLER['zh']['folders'][0]/SELLER['zh']['how_to_use']
    src=tmp_path/'how.txt';src.write_text('NEW TEXT');how.write_text('NEW TEXT')
    m['texts']['how_to_use']['zh']=str(src)
    assert any('version manifest' in p for p in check(out,m))


def test_identity_card_sources_must_be_originals(manifest,tmp_path):
    path,m,out=_built(manifest,tmp_path)
    assert not any('card' in p for p in check(out,m,path))
    sheet=Path(m['identity_card']['zh']['path']+'.sheet.json');saved=sheet.read_text()
    try:
        d=json.loads(saved);walk=m['motion']['walk']
        d['sources'][1]=dict(path=walk['path'],sha256=walk['sha256'],label='04')
        sheet.write_text(json.dumps(d))
        assert any('identity_card.zh' in p and 'not an original' in p for p in check(out,m,path))
    finally: sheet.write_text(saved)


# --- Final review round 2 (codex-review e7c786d): blocking findings, each reproduced first ---

def test_lookset_symlink_does_not_skip_hash_checks(manifest,tmp_path):
    path,m,out=_built(manifest,tmp_path,lookset=True)
    d2=out/names(m)['engineering']/names(m)['lookset']
    (d2/'supplements/12.png').unlink();(d2/'supplements/12.png').symlink_to(m['motion']['walk']['path'])
    shutil.copyfile(m['motion']['sit']['path'],d2/'supplements/11.png')
    problems=check(out,m,path,True)
    assert any('12.png' in p for p in problems) and any('11.png' in p for p in problems), problems


def test_png_header_plus_text_is_not_an_image(manifest,tmp_path):
    path,m=manifest
    fake=tmp_path/'fake.png';fake.write_bytes(b'\x89PNG\r\n\x1a\n'+b'INTERNAL RECORDS')
    raw=json.loads(path.read_text());raw['originals']['12']=dict(path=str(fake),sha256=hashlib.sha256(fake.read_bytes()).hexdigest())
    path.write_text(json.dumps(raw,ensure_ascii=False))
    result=invoke('build_pack.py','--manifest',path,'--out-dir',tmp_path/'packs')
    assert result.returncode!=0 and 'not a PNG' in result.stderr+result.stdout


def test_card_sheet_with_empty_sources_is_a_problem(manifest,tmp_path):
    path,m,out=_built(manifest,tmp_path)
    sheet=Path(m['identity_card']['zh']['path']+'.sheet.json');saved=sheet.read_text()
    try:
        d=json.loads(saved);d['sources']=[];sheet.write_text(json.dumps(d))
        assert any('identity_card.zh' in p for p in check(out,m,path))
    finally: sheet.write_text(saved)


def test_reshaped_crop_is_not_an_exact_crop(tmp_path):
    from PIL import Image
    import check_pack
    src=tmp_path/'o.png';Image.new('RGB',(8,8),(10,20,30)).save(src)
    with Image.open(src) as im: im.putpixel((1,1),(200,0,0))
    a=Image.open(src).convert('RGB');a.putpixel((1,1),(200,0,0));a.save(src)
    crop=a.crop((0,0,4,4));reshaped=Image.frombytes('RGB',(2,8),crop.tobytes());out=tmp_path/'c.png';reshaped.save(out)
    assert not check_pack.same_crop(src,[0,0,4,4],out)
    crop.save(out);assert check_pack.same_crop(src,[0,0,4,4],out)
