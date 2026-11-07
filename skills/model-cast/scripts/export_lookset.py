"""Export only through the pinned, unmodified Lookset exporter."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from gen_request import sha256
from pack_common import load_manifest, verify_sources, IDS

VENDOR=Path(__file__).resolve().parents[1]/'vendor/lookset'
LOCKS={'model_reference.py':'a471ac6f9d3356c2dca1e0250a85d6eef2e94fd3eefafb80e9de8e94b320b465',
       'model-reference.py':'45994685210b898117589b2dedb4a1bc735c5b2a7258f45ab14d6d0e780d2ad5'}


def verify_vendor():
    data=json.loads((VENDOR/'VENDOR.json').read_text())
    rows={r['path']:r['sha256'] for r in data['files']}
    for name,wanted in LOCKS.items():
        actual=sha256(VENDOR/name)
        if actual!=wanted or rows.get(name)!=wanted:
            raise ValueError(f'vendor hash mismatch: {name} actual={actual} declared={rows.get(name)} locked={wanted}')


def export(m,out):
    verify_vendor()
    try: import PIL  # noqa: F401 -- dependency gate, no installation
    except ImportError as e: raise ValueError('tool-blocked: Pillow unavailable') from e
    output = Path(out).resolve()
    internal = Path(m['run_dir']).resolve() / 'c8'
    if internal == output or output in internal.parents:
        raise ValueError('run_dir must be outside Lookset package')
    verify_sources(m)
    if Path(out).exists(): raise ValueError('target already exists')
    d=m['lookset']
    spec=dict(name=m['model_name'],confirmation_note=d['confirmation_note'],
              model=dict(source_type='ai',scope='full',subject='adult female model',locked=d['locked'],
                         adjustable=d['adjustable'],styling_lock=d['styling_lock']),
              references=[m['originals']['P3-2']['path']],
              supplements=[dict(m['originals'][i],scope='face' if i in ('01','02','03') else 'full',
                                confirmation_note=d['supplement_notes'][i]) for i in ['01','04']+[i for i in IDS if i not in ('01','04')]])
    # Evidence is version-named and never overwritten (V1.0 files stay read-only).
    internal=Path(m['run_dir'])/'c8';internal.mkdir(parents=True,exist_ok=True)
    spec_path=internal/f'lookset-spec-{m["version"]}.json';validate_path=internal/f'lookset-validate-{m["version"]}.json'
    if spec_path.exists() or validate_path.exists(): raise ValueError('Lookset evidence for this version already exists: '+str(spec_path))
    with spec_path.open('x') as stream: stream.write(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    base=['python3','-B',str(VENDOR/'model-reference.py')]
    result=subprocess.run(base+['export','--package',str(Path(out).resolve()),'--spec',str(spec_path)],env=env,text=True,capture_output=True)
    print(result.stdout,end='');print(result.stderr,end='')
    if result.returncode: return result.returncode
    result=subprocess.run(base+['validate','--package',str(Path(out).resolve())],env=env,text=True,capture_output=True)
    with validate_path.open('x') as stream: stream.write(result.stdout)
    print(result.stdout,end='');print(result.stderr,end='')
    return result.returncode


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',required=True);p.add_argument('--out',required=True)
    a=p.parse_args()
    try: return export(load_manifest(a.manifest),a.out)
    except (OSError,ValueError,KeyError,TypeError) as e: p.error(str(e))


if __name__=='__main__': raise SystemExit(main())
