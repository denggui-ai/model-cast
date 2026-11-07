"""Aggregate existing run evidence verbatim; add no judgments.

Section 1 shows only the confirmed formal selection calls (--selection-ids);
other candidate receipts are listed separately as history, never merged in.
"""
import argparse
import json
from pathlib import Path
from gen_request import sha256

IDENTITY_PURPOSES = ('face01', 'body04', 'face_angle', 'body_angle', 'motion', 'diagram')


def outputs(r):
    paths = [o.get('output_path') for o in r.get('outputs') or [] if o.get('output_path')]
    if r.get('output_path') and r['output_path'] not in paths:
        paths.append(r['output_path'])
    return paths


def build(root, selection_ids):
    root=Path(root).resolve()
    receipts={}
    for path in sorted(root.rglob('receipt.json')):
        r=json.loads(path.read_text())
        if r['id'] in receipts: raise ValueError('duplicate receipt id: '+r['id'])
        receipts[r['id']]=r
    missing=[i for i in selection_ids if i not in receipts]
    if missing: raise ValueError('selection ids without receipt: '+','.join(missing))
    wrong=[i for i in selection_ids if receipts[i].get('purpose')!='candidate']
    if wrong: raise ValueError('selection ids are not candidate receipts: '+','.join(wrong))
    formal=[receipts[i] for i in selection_ids]
    sections=['# 1. 选人过程\n','## c4/selection.md\n',(root/'c4/selection.md').read_text()]
    prompts=sorted({r['prompt_path'] for r in formal})
    sections += ['## 正式选人提示词（'+str(len(prompts))+' 份）\n']
    for prompt in prompts: sections += ['`'+prompt+'`\n',Path(prompt).read_text()]
    sections += ['## 正式候选（'+str(len(formal))+' 张）\n']
    for r in formal:
        sections += [json.dumps({k:r.get(k) for k in ('id','status','prompt_sha256')}|{'outputs':outputs(r)},ensure_ascii=False)]
    history=[r for i,r in sorted(receipts.items()) if r.get('purpose') in ('candidate','draft') and i not in selection_ids]
    sections += ['## 历史候选试验（不属于正式选人，只列出处）\n']
    for r in history:
        sections += [json.dumps({k:r.get(k) for k in ('id','purpose','status')},ensure_ascii=False)]
    sections += ['\n# 2. 定人和补角度的生成记录\n']
    identity=[r for _,r in sorted(receipts.items()) if r.get('purpose') in IDENTITY_PURPOSES]
    for r in identity:
        sections += [json.dumps({k:r.get(k) for k in ('id','purpose','refs','prompt_sha256','status','codex_cli_version')},ensure_ascii=False)]
    sections += ['\n# 3. 自检结论（原文）\n']
    for name in ('c6/selfcheck.md','n2/selfcheck.md'):
        sections += ['## '+name+'\n',(root/name).read_text()]
    sections += ['\n# 4. 版本清单（正式候选与第 2 段调用的输出）\n']
    for r in formal+identity:
        for out in outputs(r):
            p=Path(out)
            sections += [str(p.relative_to(root) if root in p.resolve().parents else p)+' '+(sha256(p) if p.is_file() else 'MISSING')]
    return '\n\n'.join(sections)+'\n'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run-dir',required=True)
    p.add_argument('--selection-ids',required=True,help='comma-separated receipt ids of the confirmed formal selection round')
    a=p.parse_args()
    ids=[i.strip() for i in a.selection_ids.split(',') if i.strip()]
    try:
        if not ids: raise ValueError('selection ids required')
        text=build(a.run_dir,ids)
        out=Path(a.run_dir)/'c7/records.md';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(text)
    except (OSError,ValueError,KeyError,TypeError) as e: p.error(str(e))
    print(out)


if __name__=='__main__': main()
