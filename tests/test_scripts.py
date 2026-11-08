import hashlib
import json
import os
import shlex
import shutil
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import zlib

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/model-cast/scripts'
FIXTURE = Path(__file__).parent / 'fixtures/t0-events-sample.jsonl'


def invoke(script, *args, home=None):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    if home:
        env['HOME'] = str(home)
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                          env=env, text=True, capture_output=True)


def png(path, width=1024, height=1536):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 0, 0, 0, 0)) +
                     chunk(b'IDAT', zlib.compress((b'\0' + b'\0' * width) * height)) + chunk(b'IEND', b''))
    return path


@pytest.fixture
def tmp_path():
    # Keep even ephemeral test artifacts inside the authorized worktree.
    with tempfile.TemporaryDirectory(prefix='model-cast-test-', dir=Path(__file__).parent) as directory:
        yield Path(directory)


@pytest.fixture
def call(tmp_path):
    home = tmp_path / 'home'
    home.mkdir()
    root = tmp_path / 'run'
    prompt = tmp_path / 'prompt.txt'
    prompt.write_text('fake prompt; no generation')
    ref = png(tmp_path / 'ref.png')
    result = invoke('gen_request.py', '--task', 'T2', '--purpose', 'candidate', '--id', 'test-1',
                    '--prompt-file', prompt, '--ref', f'selection={ref}', '--run-dir', root)
    assert result.returncode == 0, result.stderr
    request = root / 'test-1/request.json'
    events = tmp_path / 'events.jsonl'
    events.write_bytes(FIXTURE.read_bytes())
    rows = [json.loads(line) for line in events.read_text().splitlines()]
    thread = next(row['thread_id'] for row in rows if row['type'] == 'thread.started')
    directory = home / '.codex/generated_images' / thread
    before = tmp_path / 'before.txt'
    before.write_text(str(home / '.codex/generated_images/other/old.png') + '\n')
    return dict(home=home, root=root, prompt=prompt, ref=ref, request=request,
                events=events, directory=directory, before=before)


def collect(call, exit_code=0):
    result = invoke('collect_receipt.py', '--request', call['request'], '--before', call['before'],
                    '--exit-code', exit_code, '--events', call['events'], home=call['home'])
    assert result.returncode == 0, result.stderr
    receipt = json.loads(result.stdout)
    rows = [json.loads(line) for line in (call['root'] / 'quota.jsonl').read_text().splitlines()]
    assert rows == [receipt]
    assert json.loads((call['request'].parent / 'receipt.json').read_text()) == receipt
    return receipt


@pytest.mark.parametrize('mode', ['none', 'missing', 'koreatest'])
def test_invalid_reference_exits_two(tmp_path, mode):
    prompt = tmp_path / 'prompt.txt'
    prompt.write_text('test')
    args = []
    if mode == 'missing':
        args = ['--ref', 'selection=' + str(tmp_path / 'absent.png')]
    if mode == 'koreatest':
        args = ['--ref', 'product=' + str(png(tmp_path / 'koreatest/2.png'))]
    result = invoke('gen_request.py', '--task', 'T2', '--purpose', 'candidate', '--id', 'test',
                    '--prompt-file', prompt, '--run-dir', tmp_path / 'run', *args)
    assert result.returncode == 2
    assert not (tmp_path / 'run').exists()


def test_request_is_explicit_and_does_not_execute(call):
    row = json.loads(call['request'].read_text())
    assert row['argv'][:2] == ['codex', 'exec']
    index = row['argv'].index('--disable')
    assert row['argv'][index:index + 3] == ['--disable', 'plugins', '--json']
    assert row['argv'][row['argv'].index('-i') + 1] == str(call['ref'])
    assert row['codex_cli_version'] == 'codex-cli 0.161.0'
    assert len(row['refs'][0]['sha256']) == 64
    assert not list(call['root'].rglob('events.jsonl'))


def test_prompt_sent_content_hashes_and_stdin(tmp_path):
    prompt = tmp_path / 'prompt.txt'
    prompt.write_bytes('正文第一行\r\n第二行\n'.encode('utf-8'))
    result = invoke('gen_request.py', '--task', 'T0', '--purpose', 't0', '--id', 'sent-1',
                    '--prompt-file', prompt, '--run-dir', tmp_path / 'run')
    assert result.returncode == 0, result.stderr
    request = json.loads((tmp_path / 'run/sent-1/request.json').read_text())
    sent = tmp_path / 'run/sent-1/prompt-sent.txt'
    prefix = '【宿主指令】不要调用任何技能、插件或脚本，不要读写文件；使用内置图片生成工具完成下面的请求，生成且只生成 1 张图。'
    assert sent.read_bytes() == (prefix + '\n请求：').encode('utf-8') + prompt.read_bytes()
    assert request['prompt_path'] == str(prompt)
    assert request['prompt_sent_path'] == str(sent)
    assert request['prompt_sha256'] == hashlib.sha256(prompt.read_bytes()).hexdigest()
    assert request['prompt_sent_sha256'] == hashlib.sha256(sent.read_bytes()).hexdigest()
    tokens = shlex.split(result.stdout)
    assert tokens[tokens.index('<') + 1] == str(sent)


@pytest.mark.parametrize('command,contaminated', [
    ('cat /Users/test/.codex/plugins/cache/threadtruth-studio/SKILL.md', True),
    ('cat /Users/test/.codex/skills/other/SKILL.md', True),
    ('python3 /Users/test/.codex/plugins/tool.py', True),
    ('cat /Users/test/.codex/skills/.system/imagegen/SKILL.md', False),
    ('cat ~/.codex/skills/.system/imagegen/SKILL.md', False),
    ('cat ~/.codex/skills/other/SKILL.md', True),
    ('cat ~/.codex/skills/.system/imagegen/SKILL.md ~/.codex/skills/other/SKILL.md', True),
    ('cat /Users/test/.codex/skills/.system/imagegen/SKILL.md /other/SKILL.md', True),
])
def test_generation_contamination(call, command, contaminated):
    with call['events'].open('a') as stream:
        for event_type in ('item.started', 'item.completed'):
            stream.write(json.dumps(dict(type=event_type, item=dict(
                type='command_execution', command=command))) + '\n')
    png(call['directory'] / 'new.png')
    row = collect(call)
    assert row['status'] == ('contaminated' if contaminated else 'ok')
    assert row['failure_class'] == (5 if contaminated else None)
    assert row['contamination'] == ([command] if contaminated else [])
    assert row['images_generated'] == 1
    assert Path(row['outputs'][0]['output_path']).exists()
    request = json.loads(call['request'].read_text())
    for key in ('prompt_path', 'prompt_sha256', 'prompt_sent_path', 'prompt_sent_sha256'):
        assert row[key] == request[key]
    assert invoke('quota.py', '--run-dir', call['root']).stdout == 'used=1 remaining=499\n'


@pytest.mark.parametrize('exit_code,count,width,expected', [
    (1, 1, 1024, 'tool_error'), (0, 0, 1024, 'contaminated'),
    (0, 2, 1024, 'contaminated'), (0, 1, 800, 'contaminated'),
])
def test_contamination_priority(call, exit_code, count, width, expected):
    with call['events'].open('a') as stream:
        stream.write(json.dumps(dict(item=dict(type='command_execution',
                                               command='cat /other/SKILL.md'))) + '\n')
    for index in range(count):
        png(call['directory'] / f'{index}.png', width, 1536)
    row = collect(call, exit_code=exit_code)
    assert row['status'] == expected
    assert row['failure_class'] == 5
    assert row['images_generated'] == count
    assert len(row['outputs']) == count


def test_synthetic_events_contaminated(call):
    # Use a minimal synthetic event stream; never depend on private local RUN data.
    source = Path(__file__).parent / 'fixtures' / 'synthetic-contaminated-events.jsonl'
    shutil.copyfile(source, call['events'])
    assert call['events'].read_bytes() == source.read_bytes()
    events = [json.loads(line) for line in call['events'].read_text().splitlines() if line.strip()]
    thread = next(event['thread_id'] for event in events if event['type'] == 'thread.started')
    png(call['home'] / '.codex/generated_images' / thread / 'new.png')
    row = collect(call)
    assert row['status'] == 'contaminated'
    assert row['failure_class'] == 5
    assert any('threadtruth-studio/' in command and 'SKILL.md' in command
               for command in row['contamination'])
    assert row['images_generated'] == 1
    assert Path(row['outputs'][0]['output_path']).exists()


@pytest.mark.parametrize('subdirectory', ['', 'casting/outputs'])
def test_check_run_accepts_only_call_directory_output_copies(call, subdirectory):
    png(call['directory'] / 'new.png')
    row = collect(call)
    output = Path(row['output_path'])
    copy = output.parent / subdirectory / 'look-1.png'
    copy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(output, copy)
    assert invoke('check_run.py', '--run-dir', call['root']).stdout == '0 problems\n'
    shutil.copyfile(output, call['root'] / 'elsewhere.png')
    png(copy, 1025, 1536)
    result = invoke('check_run.py', '--run-dir', call['root'])
    assert result.returncode == 1
    assert 'elsewhere.png: missing receipt' in result.stdout
    assert f'{copy}: missing receipt' in result.stdout


def test_no_image(call):
    row = collect(call)
    assert row['status'] == 'no_image'
    assert row['images_generated'] == 0
    assert row['output_path'] is None


def test_multi_image_preserves_and_counts_all(call):
    png(call['directory'] / 'one.png')
    png(call['directory'] / 'two.png')
    row = collect(call)
    assert row['status'] == 'multi_image'
    assert row['images_generated'] == 2
    assert row['output_path'] is None
    assert [Path(o['output_path']).name for o in row['outputs']] == ['test-1-1.png', 'test-1-2.png']
    assert all(Path(o['output_path']).exists() for o in row['outputs'])
    result = invoke('quota.py', '--run-dir', call['root'])
    assert result.stdout == 'used=2 remaining=498\n'
    assert invoke('check_run.py', '--run-dir', call['root']).returncode == 0


@pytest.mark.parametrize('width,height', [(800, 1200), (1536, 1024), (1600, 1536)])
def test_size_fail(call, width, height):
    png(call['directory'] / 'one.png', width, height)
    row = collect(call)
    assert row['status'] == 'size_fail'
    assert row['failure_class'] == 6
    assert row['images_generated'] == 1
    assert row['output_path'] is None
    assert len(row['outputs']) == 1
    assert invoke('check_run.py', '--run-dir', call['root']).returncode == 1


@pytest.mark.parametrize('mode', ['missing', 'empty'])
def test_before_missing_or_empty_is_tool_error(call, mode):
    if mode == 'missing':
        call['before'].unlink()
    else:
        call['before'].write_text('')
    assert collect(call)['status'] == 'tool_error'


def test_other_sessions_and_existing_images_excluded(call):
    old = png(call['directory'] / 'old.png')
    unrelated = png(call['directory'].parent / 'other/new.png')
    call['before'].write_text(str(old) + '\n' + str(unrelated) + '\n')
    png(call['directory'].parent / 'other/after.png')
    png(call['directory'] / 'new.png')
    row = collect(call)
    assert row['status'] == 'ok'
    assert row['images_generated'] == 1
    assert row['source_generated_path'].endswith('/new.png')


def test_hash_mismatch_and_missing_coverage(call):
    png(call['directory'] / 'new.png')
    row = collect(call)
    assert invoke('check_run.py', '--run-dir', call['root']).stdout == '0 problems\n'
    call['ref'].write_bytes(b'changed')
    Path(row['output_path']).write_bytes(b'corrupt')
    png(call['root'] / 'orphan.png')
    result = invoke('check_run.py', '--run-dir', call['root'])
    assert result.returncode == 1
    assert 'reference hash mismatch' in result.stdout
    assert 'output hash mismatch' in result.stdout
    assert 'missing receipt' in result.stdout


def test_quota_legacy_and_actual_counts(tmp_path):
    (tmp_path / 'quota.jsonl').write_text('\n'.join(map(json.dumps, [
        dict(counts_quota=True), dict(counts_quota=False), dict(images_generated=0),
        dict(images_generated=2, counts_quota=True), dict(images_generated=1)])) + '\n')
    result = invoke('quota.py', '--run-dir', tmp_path)
    assert result.returncode == 0
    assert result.stdout == 'used=4 remaining=496\n'


def test_nonzero_exit_preserves_images(call):
    png(call['directory'] / 'new.png')
    row = collect(call, exit_code=1)
    assert row['status'] == 'tool_error'
    assert row['images_generated'] == 1
    assert len(row['outputs']) == 1


def test_duplicate_collection_does_not_double_count(call):
    collect(call)
    result = invoke('collect_receipt.py', '--request', call['request'], '--before', call['before'],
                    '--exit-code', 0, '--events', call['events'], home=call['home'])
    assert result.returncode == 2
    assert len((call['root'] / 'quota.jsonl').read_text().splitlines()) == 1


def test_face_and_t0_dimensions(call):
    request = json.loads(call['request'].read_text())
    request['purpose'] = 'face01'
    call['request'].write_text(json.dumps(request))
    png(call['directory'] / 'new.png', 1024, 1024)
    assert collect(call)['status'] == 'ok'


def test_t0_landscape_allowed(call):
    request = json.loads(call['request'].read_text())
    request['purpose'] = 't0'
    call['request'].write_text(json.dumps(request))
    png(call['directory'] / 'new.png', 1536, 1024)
    assert collect(call)['status'] == 'ok'


def test_invalid_events_is_tool_error(call):
    call['events'].write_text('{bad json')
    assert collect(call)['status'] == 'tool_error'


def test_invalid_png_still_retains_all_generated_outputs(call):
    call['directory'].mkdir(parents=True)
    (call['directory'] / 'a.png').write_bytes(b'invalid PNG')
    png(call['directory'] / 'b.png')
    row = collect(call)
    assert row['status'] == 'tool_error'
    assert row['images_generated'] == 2
    assert len(row['outputs']) == 2
    assert all(Path(o['output_path']).is_file() for o in row['outputs'])


def test_t0_request_without_references(tmp_path):
    prompt = tmp_path / 'prompt.txt'
    prompt.write_text('fake prompt')
    result = invoke('gen_request.py', '--task', 'T0', '--purpose', 't0', '--id', 't0-1',
                    '--prompt-file', prompt, '--run-dir', tmp_path / 'run')
    assert result.returncode == 0
    row = json.loads((tmp_path / 'run/t0-1/request.json').read_text())
    assert row['refs'] == []
    assert '-i' not in row['argv']


@pytest.mark.parametrize('role,purpose,exit_code', [
    ('product', 'candidate', 2), ('product', 'draft', 2),
    ('body04', 'draft', 2), ('selection', 'tryon', 2),
    ('product', 'tryon', 0), ('product', 'tryon_fix', 0),
])
def test_koreatest_role_and_purpose(tmp_path, role, purpose, exit_code):
    prompt = tmp_path / 'prompt.txt'
    prompt.write_text('fake prompt')
    ref = png(tmp_path / 'koreatest/product.png')
    root = tmp_path / 'run'
    result = invoke('gen_request.py', '--task', 'T6', '--purpose', purpose, '--id', 'test',
                    '--prompt-file', prompt, '--ref', f'{role}={ref}', '--run-dir', root)
    assert result.returncode == exit_code, result.stderr
    assert (root / 'test/request.json').exists() == (exit_code == 0)


@pytest.fixture
def cropped(tmp_path):
    source = png(tmp_path / 'source.png', 100, 120)
    output = tmp_path / 'run/face.png'
    result = invoke('crop.py', '--src', source, '--box', '10,20,80,100', '--out', output)
    assert result.returncode == 0, result.stderr
    return source, output


def test_crop_provenance_and_no_resize(cropped):
    import hashlib
    source, output = cropped
    record = json.loads(Path(str(output) + '.crop.json').read_text())
    assert record == dict(source_path=str(source),
                          source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                          box=[10, 20, 80, 100],
                          output_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                          width=70, height=80)
    assert output.read_bytes()[:8] == b'\x89PNG\r\n\x1a\n'
    assert struct.unpack('>II', output.read_bytes()[16:24]) == (70, 80)
    assert not (output.parent / 'quota.jsonl').exists()


@pytest.mark.parametrize('box', ['-1,0,20,20', '0,0,101,20', '0,0,20,121',
                                      '20,20,10,30', '0,0,0,20'])
def test_crop_out_of_bounds(tmp_path, box):
    source = png(tmp_path / 'source.png', 100, 120)
    output = tmp_path / 'face.png'
    result = invoke('crop.py', '--src', source, f'--box={box}', '--out', output)
    assert result.returncode == 2
    assert not output.exists()
    assert not Path(str(output) + '.crop.json').exists()


@pytest.mark.parametrize('existing', ['image', 'record'])
def test_crop_refuses_overwrite(tmp_path, existing):
    source = png(tmp_path / 'source.png', 100, 120)
    output = tmp_path / 'face.png'
    occupied = output if existing == 'image' else Path(str(output) + '.crop.json')
    occupied.write_bytes(b'keep original')
    result = invoke('crop.py', '--src', source, '--box', '10,20,80,100', '--out', output)
    assert result.returncode == 2
    assert occupied.read_bytes() == b'keep original'


def test_check_run_recognizes_crop_without_receipt(cropped):
    _, output = cropped
    result = invoke('check_run.py', '--run-dir', output.parent)
    assert result.returncode == 0, result.stdout
    assert result.stdout == '0 problems\n'


@pytest.mark.parametrize('changed,problem', [('source', 'source hash mismatch'),
                                           ('output', 'output hash mismatch')])
def test_check_run_detects_changed_crop_hashes(cropped, changed, problem):
    source, output = cropped
    (source if changed == 'source' else output).write_bytes(b'changed')
    result = invoke('check_run.py', '--run-dir', output.parent)
    assert result.returncode == 1
    assert problem in result.stdout
    assert 'missing receipt' not in result.stdout


@pytest.mark.parametrize('purpose,width,height,expected', [
    ('t0', 1000, 1500, True),
    ('candidate', 1086, 1448, True),
    ('draft', 1536, 1024, True), ('candidate', 1536, 1024, False),
    ('candidate', 1024, 1024, True), ('tryon', 1024, 1024, False),
    ('face01', 1024, 1024, True), ('body04', 1086, 1448, True),
    ('tryon', 1086, 1448, True), ('tryon_fix', 1086, 1448, True),
] + [(purpose, 1000, 1500, False) for purpose in
     ('draft', 'candidate', 'face01', 'body04', 'tryon', 'tryon_fix')])
def test_rev1_size_rules(monkeypatch, purpose, width, height, expected):
    monkeypatch.syspath_prepend(str(SCRIPTS))
    from collect_receipt import size_ok
    assert size_ok(purpose, width, height) is expected


def register(directory, *extra):
    return invoke('register_external.py', '--dir', directory, '--kind', 'chatgpt-web',
                  '--source', 'test conversation', '--note', 'test note', *extra)


def test_external_register_skip_and_hash_conflict(tmp_path):
    image = png(tmp_path / 'external.png', 20, 30)
    result = register(tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout == 'registered=1 skipped=0\n'
    manifest = tmp_path / 'EXTERNAL.json'
    original = manifest.read_bytes()
    entry, = json.loads(original)['entries']
    assert entry['file'] == image.name
    assert entry['sha256'] == hashlib.sha256(image.read_bytes()).hexdigest()
    assert (entry['width'], entry['height']) == (20, 30)
    assert entry['kind'] == 'chatgpt-web'
    assert entry['source'] == 'test conversation'
    assert entry['note'] == 'test note'
    assert entry['counts_quota'] is False
    assert entry['registered_at'].endswith('+08:00')
    assert register(tmp_path).stdout == 'registered=0 skipped=1\n'
    assert manifest.read_bytes() == original
    assert invoke('quota.py', '--run-dir', tmp_path).stdout == 'used=0 remaining=500\n'
    assert invoke('check_run.py', '--run-dir', tmp_path).stdout == '0 problems\n'
    png(image, 21, 30)
    assert register(tmp_path).returncode == 2
    assert manifest.read_bytes() == original
    result = invoke('check_run.py', '--run-dir', tmp_path)
    assert result.returncode == 1
    assert 'external hash mismatch' in result.stdout
    assert 'missing receipt' not in result.stdout
    assert 'size_fail' not in result.stdout


def test_external_explicit_files_and_missing_file(tmp_path):
    png(tmp_path / 'one.png')
    png(tmp_path / 'two.png')
    assert register(tmp_path, '--file', 'absent.png').returncode == 2
    assert not (tmp_path / 'EXTERNAL.json').exists()
    result = register(tmp_path, '--file', 'one.png')
    assert result.returncode == 0, result.stderr
    assert [e['file'] for e in json.loads((tmp_path / 'EXTERNAL.json').read_text())['entries']] == ['one.png']


def test_external_default_excludes_receipts_crops_and_nested(call):
    png(call['directory'] / 'new.png')
    row = collect(call)
    output = Path(row['output_path'])
    shutil.copyfile(output, output.parent / 'copy.png')
    png(output.parent / 'nested/unregistered.png')
    crop = png(output.parent / 'crop.png')
    Path(str(crop) + '.crop.json').write_text('{}')
    png(output.parent / 'external.png', 10, 10)
    result = register(output.parent)
    assert result.returncode == 0, result.stderr
    assert [e['file'] for e in json.loads((output.parent / 'EXTERNAL.json').read_text())['entries']] == ['external.png']


def test_check_run_recomputes_historical_size_fail(call):
    png(call['directory'] / 'new.png', 1086, 1448)
    collect(call)
    receipt = call['request'].parent / 'receipt.json'
    data = json.loads(receipt.read_text())
    data['status'] = 'size_fail'
    receipt.write_text(json.dumps(data))
    original = receipt.read_bytes()
    assert invoke('check_run.py', '--run-dir', call['root']).stdout == '0 problems\n'
    assert receipt.read_bytes() == original


def test_rev2_fixed_casting_sentence_matches_p3():
    # Exact second line from P3; keep the regression independent of RUN availability.
    expected = (
        '这一步的任务是选人，不是还原衣服：衣服细节以后另有人负责，提示词里一句“穿参考图这件衣服”就够。'
        '你的重心是这位模特本人——选一个买这件衣服的顾客会觉得好看、愿意点进来的人。'
    ).encode('utf-8')
    prompts = SCRIPTS.parent / 'references/phase1-prompts.md'
    assert b'> ' + expected in prompts.read_bytes().splitlines()


def test_gen_request_example_uses_product_reference():
    skill = (SCRIPTS.parent / 'SKILL.md').read_text()
    examples = [shlex.split(line) for line in skill.splitlines()
                if line.startswith('python3 scripts/gen_request.py ')]
    assert examples
    for command in examples:
        refs = [command[index + 1] for index, token in enumerate(command) if token == '--ref']
        assert refs
        assert all(ref.startswith('product=') for ref in refs)


@pytest.mark.parametrize('purpose,w,h,ok', [
    ('face_angle',1024,1024,True), ('face_angle',1536,1024,True),
    ('body_angle',1024,1536,True), ('body_angle',1024,1024,False),
    ('motion',1024,1024,True), ('motion',1536,1024,False),
    ('diagram',1536,1024,True), ('diagram',1024,1000,False),
] + [(p,1000,1536,False) for p in ('face_angle','body_angle','motion','diagram')])
def test_phase2_size(monkeypatch,purpose,w,h,ok):
    monkeypatch.syspath_prepend(str(SCRIPTS))
    from collect_receipt import size_ok
    assert size_ok(purpose,w,h) is ok


@pytest.mark.parametrize('mode', ['ok','missing_lock','missing_ref','reverse','path','hash','extra','missing_key','bad_hash','bad_points'])
def test_identity_lock(tmp_path,mode):
    refs = [png(tmp_path / f'{i}.png') for i in range(3)]
    lock = dict(schema=1, memory_points_zh=['a','b'], **{
        role: dict(path=str(ref),sha256=hashlib.sha256(ref.read_bytes()).hexdigest())
        for role,ref in zip(('face01','body04'),refs)})
    arguments = ['--ref',f'face01={refs[0]}','--ref',f'body04={refs[1]}']
    if mode == 'missing_ref': arguments = arguments[:2]
    if mode == 'reverse': arguments = arguments[2:] + arguments[:2]
    if mode == 'path': arguments[1] = f'face01={refs[2]}'
    if mode == 'hash': lock['face01']['sha256'] = '0'*64
    if mode == 'extra': lock['extra'] = 1
    if mode == 'missing_key': del lock['body04']['path']
    if mode == 'bad_hash': lock['face01']['sha256'] = 'bad'
    if mode == 'bad_points': lock['memory_points_zh'] = ['a']
    path = tmp_path / 'lock.json'; path.write_text(json.dumps(lock))
    prompt = tmp_path / 'prompt.txt'; prompt.write_text('test')
    if mode != 'missing_lock': arguments += ['--identity-lock',path]
    result = invoke('gen_request.py','--task','T8','--purpose','face_angle','--id','face-1',
                    '--prompt-file',prompt,'--run-dir',tmp_path/'run',*arguments)
    assert result.returncode == (0 if mode == 'ok' else 2), result.stderr


@pytest.mark.parametrize('with_ref',[True,False])
def test_diagram_refs(tmp_path,with_ref):
    prompt = tmp_path/'prompt.txt'; prompt.write_text('test')
    args = ['--ref',f'face01={png(tmp_path/"ref.png")}'] if with_ref else []
    result = invoke('gen_request.py','--task','T9','--purpose','diagram','--id','diagram-1',
                    '--prompt-file',prompt,'--run-dir',tmp_path/'run',*args)
    assert result.returncode == (2 if with_ref else 0), result.stderr


def test_sheet_hashes(tmp_path):
    from PIL import Image
    source = tmp_path/'source.png'; Image.new('RGB',(20,30),'red').save(source)
    out = tmp_path/'run/sheet.png'
    result = invoke('compose_sheet.py','--out',out,'--cols',2,'--cell','100x100','--item',f'{source}=01 正面')
    assert result.returncode == 0, result.stderr
    assert invoke('check_run.py','--run-dir',out.parent).stdout == '0 problems\n'
    source.write_bytes(b'changed')
    assert 'source hash mismatch' in invoke('check_run.py','--run-dir',out.parent).stdout
    out.write_bytes(b'changed')
    assert 'output hash mismatch' in invoke('check_run.py','--run-dir',out.parent).stdout
