"""Build the V3 zh pack, en pack and engineering folder from a validated manifest; never modify sources."""
import argparse
import json
from pathlib import Path
import shutil
from gen_request import sha256
from pack_common import (ANGLES, LANGS, UPLOAD_IDS, engineering_layout, joined_text, load_manifest, names,
                         seller_layout, verify_sources, version_manifest_name)


def copy(source, output, expected, where):
    shutil.copyfile(source, output)
    actual = sha256(output)
    if actual != (expected or sha256(source)): raise OSError(where+': copied hash mismatch')
    return actual


def build(m, out_dir, manifest_path=None):
    out = Path(out_dir).resolve(); n = names(m)
    targets = [out/n['zh'], out/n['en'], out/n['engineering']]
    for target in targets:
        if target.exists(): raise ValueError('target already exists: '+str(target))
    internal = Path(m['run_dir']).resolve() / 'c8'
    for target in targets:
        if internal == target or target in internal.parents:
            raise ValueError('run_dir must be outside seller package')
    version_path = internal / version_manifest_name(m)
    if version_path.exists(): raise ValueError('version manifest already exists (versions are never overwritten): '+str(version_path))
    verify_sources(m)
    records = []
    created = []
    try:
        for lang,target in zip(LANGS, targets):
            target.mkdir(parents=True); created.append(target)
            for dest,spec in seller_layout(m, lang).items():
                output = target/dest; output.parent.mkdir(parents=True, exist_ok=True)
                if spec[0] == 'copy':
                    actual = copy(spec[1], output, spec[2], dest); original_id = spec[3]
                elif spec[0] == 'text':
                    output.write_text(joined_text(spec[1]), encoding='utf-8'); actual = sha256(output); original_id = None
                records.append(dict(package=target.name, path=dest, sha256=actual, original_id=original_id))
        engineering = targets[2]; engineering.mkdir(parents=True); created.append(engineering)
        layout = engineering_layout(m)
        for dest,spec in layout.items():
            if spec[0] == 'copy':
                output = engineering/dest; output.parent.mkdir(parents=True, exist_ok=True)
                records.append(dict(package=engineering.name, path=dest, sha256=copy(spec[1], output, spec[2], dest), original_id=None))
        upload_rows = [dict(filename=f'{i}_{ANGLES[i]}.png', sha256=m['originals'][i]['sha256']) for i in UPLOAD_IDS]
        version = dict(packages=[t.name for t in targets], version=m['version'], files=records, upload_files=upload_rows)
        text = json.dumps(version, ensure_ascii=False, indent=2) + '\n'
        for dest,spec in layout.items():
            output = engineering/dest; output.parent.mkdir(parents=True, exist_ok=True)
            if spec[0] == 'manifest':
                if manifest_path: shutil.copyfile(manifest_path, output)
                else: output.write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            elif spec[0] == 'version':
                output.write_text(text, encoding='utf-8')
        internal.mkdir(parents=True, exist_ok=True)
        with version_path.open('x', encoding='utf-8') as stream:
            created.append(version_path)  # only after 'x' succeeded: never remove a file we did not create
            stream.write(text)
    except Exception:
        for target in created:
            if target.is_dir(): shutil.rmtree(target)
            elif target.exists(): target.unlink()
        raise
    return targets


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',required=True);p.add_argument('--out-dir',required=True)
    a=p.parse_args()
    try:
        for target in build(load_manifest(a.manifest),a.out_dir,a.manifest): print(target)
    except (ValueError,KeyError,TypeError) as e: p.error(str(e))
    except OSError as e:
        print(str(e));return 1
    return 0


if __name__=='__main__': raise SystemExit(main())
