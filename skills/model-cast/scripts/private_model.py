#!/usr/bin/env python3
"""One private adult AI candidate; native generation is performed by the host tool.

Reuses the existing ledger and ThreadTruth model-reference contract. No network,
public roster writes, automatic retries, image acceptance or publication.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
import ledger

ROOT = Path(__file__).resolve().parent.parent


def reference_api(skill_dir):
    path = Path(skill_dir).expanduser().resolve() / "scripts" / "model_reference.py"
    spec = importlib.util.spec_from_file_location("model_cast_reference", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in ("validate_model", "validate_image", "prompt_lines", "digest", "export_package", "load_package"):
        if not callable(getattr(module, name, None)):
            raise ValueError("ThreadTruth model-reference interface unavailable: " + name)
    return module


def private_root(path):
    root = Path(path).expanduser().resolve()
    if root == ROOT or root.is_relative_to(ROOT):
        raise ValueError("Choose a private task directory outside the model-cast skill/repository")
    return root


def write_new(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def note(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Record the actual user statement/source, not an empty note")
    return value.strip()


def image_paths(root, rows, api):
    paths = []
    for row in rows:
        path = (root / row["file"]).resolve()
        if not path.is_relative_to(root) or api.digest(path) != row["sha256"]:
            raise ValueError("Missing or changed task image")
        api.validate_image(path)
        paths.append(str(path))
    return paths


def prepare(task, spec, api):
    root = private_root(task)
    if set(spec) != {"model", "view", "references", "source_note"}:
        raise ValueError("Spec requires model, view, references and source_note only")
    model = api.validate_model(spec["model"])
    if model["source_type"] not in ("new", "ai") or "styling_lock" not in model:
        raise ValueError("Private casting supports new/ai adults and requires explicit styling_lock")
    if spec["view"] not in ("face", "full"):
        raise ValueError("view must be face or full")
    if model["source_type"] == "new" and model["scope"] == "full" and spec["view"] != "full":
        raise ValueError("A new face-only image cannot establish full-body identity scope")
    refs = spec["references"]
    if not isinstance(refs, list) or len(refs) > 5:
        raise ValueError("Provide a list of at most five identity references")
    if (model["source_type"] == "new" and refs) or (model["source_type"] == "ai" and not refs):
        raise ValueError("New text casting has no references; existing AI requires original references")
    sources = [Path(p).expanduser().resolve() for p in refs]
    for path in sources:
        api.validate_image(path)
    source_note = note(spec["source_note"])
    root.mkdir(parents=True, exist_ok=False)
    # Ignore all private task contents even when the caller uses another Git workspace.
    (root / ".gitignore").write_text("*\n", encoding="utf-8")
    (root / "references").mkdir()
    rows = []
    for i, path in enumerate(sources, 1):
        relative = f"references/{i:02d}{path.suffix.lower()}"
        shutil.copyfile(path, root / relative)
        rows.append({"file": relative, "sha256": api.digest(root / relative)})
    data = {"model": model, "view": spec["view"], "references": rows, "source_note": source_note}
    write_new(root / "task.json", data)
    # Capacity is one call, not authorization. reserve requires the current user's note.
    ledger.init(root / "ledger.json", budgets={"roster_pool": 1, "shoot_pool": 0})
    return {"task": str(root), "state": "prepared", "calls": 0}


def reserve(task, authorization_note, api):
    root = private_root(task)
    if (root / "package").exists():
        raise ValueError("This task is saved; create a new candidate/version")
    data = read(root / "task.json")
    refs = image_paths(root, data["references"], api)
    authorization_note = note(authorization_note)
    view = ("Front-facing, shoulder-up portrait, unobscured face."
            if data["view"] == "face" else
            "Front-facing full body, head to shoes visible, natural proportions, "
            "arms relaxed and hands visible. Do not elongate the body or narrow the waist.")
    prompt = "\n".join([
        "Create one photographic reference of a single fictional adult model, portrait 2:3.",
        "Plain modest clothing, light-gray studio, soft light, natural perspective; no text or watermark.",
        view, *api.prompt_lines(data["model"]),
        "Follow declared appearance and hairstyle; do not force an updo or a standard fashion body.",
        *( ["Use the attached original AI identity references; requested changes are soft text constraints."] if refs else []),
    ])
    n = ledger.reserve("roster_pool", "private_model", root.name, data["view"], root / "ledger.json")
    args = {"prompt": prompt, "transparent_background": False}
    if refs:
        args["referenced_image_paths"] = refs
    request = {"call_n": n, "task_sha256": api.digest(root / "task.json"),
               "authorization_note": authorization_note, "image_gen_arguments": args}
    write_new(root / "request.json", request)
    return request


def pending_call(root, api):
    request = read(root / "request.json")
    if request["task_sha256"] != api.digest(root / "task.json"):
        raise ValueError("Task changed after reservation; restore its original inputs")
    calls = read(root / "ledger.json")["calls"]
    if len(calls) != 1 or request["call_n"] != calls[0]["n"]:
        raise ValueError("No unique reserved call to recover")
    return request["call_n"]


def returned(task, file, api):
    root = private_root(task)
    n = pending_call(root, api)
    source = Path(file).expanduser().resolve()
    details = api.validate_image(source)
    sha = api.digest(source)
    output = root / "output.json"
    if output.exists():
        row = read(output)
        image_paths(root, [row], api)
        if row["sha256"] != sha:
            raise ValueError("Cannot replace the original returned candidate")
    else:
        path = root / ("candidate" + source.suffix.lower())
        if path.exists():
            if api.digest(path) != sha:
                raise ValueError("A different candidate already exists")
        else:
            with path.open("xb") as stream:
                stream.write(source.read_bytes())
        row = {"file": path.name, "sha256": sha, "image": details}
        write_new(output, row)
    ledger.record(n, "returned", image_path=str(root / row["file"]), path=root / "ledger.json")
    return {**row, "state": "awaiting_visual_acceptance"}


def failed(task, failure_note, api):
    root = private_root(task)
    n = pending_call(root, api)
    if (root / "output.json").exists():
        raise ValueError("Candidate already returned; record visual findings without erasing it")
    write_new(root / "failure.json", {"note": note(failure_note), "call_n": n})
    ledger.record(n, "failed_or_unknown", path=root / "ledger.json")
    return {"state": "stopped", "calls": 1, "automatic_retry": False}


def save(task, name, confirmation_note, api):
    root = private_root(task)
    data = read(root / "task.json")
    confirmation_note = note(confirmation_note)
    refs = image_paths(root, data["references"], api)
    supplements = []
    output = root / "output.json"
    calls = read(root / "ledger.json")["calls"]
    if calls and not output.exists():
        raise ValueError("Reserved candidate unresolved; recover its result before saving")
    if output.exists():
        pending_call(root, api)
        row = read(output)
        candidate = image_paths(root, [row], api)[0]
        if data["model"]["source_type"] == "new":
            refs = [candidate]
        else:
            supplements = [{"path": candidate, "sha256": row["sha256"],
                            "scope": data["view"], "confirmation_note": confirmation_note}]
    if not refs:
        raise ValueError("A text direction is not an accepted image; return and review a candidate first")
    package = root / "package"
    card = api.export_package(package, data["model"], refs, name, confirmation_note,
                              supplements=supplements)
    # Keep provenance outside model.json: its schema is owned by the consumer.
    write_new(package / "source.json", {"source_note": data["source_note"],
                                       "storage": "private", "automatic_license_grant": False})
    (package / "SOURCE.md").write_text(
        "私人保存的人物包；本操作不授予 CC0 或独家权利，既有来源许可仍有效。\n\n"
        + data["source_note"] + "\n\n"
        + "AI 生成的虚构成年人物；不保证与现实人物绝不相似、精确尺码或跨商品身份稳定。\n",
        encoding="utf-8")
    return {"package": str(package), "source_type": card["model"]["source_type"],
            "references": len(card["references"]), "supplements": len(card.get("supplements", []))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "reserve", "returned", "failed", "save"])
    parser.add_argument("--task", required=True, type=Path)
    parser.add_argument("--threadtruth", required=True, type=Path, help="Actual ThreadTruth skill directory")
    parser.add_argument("--spec", type=Path)
    parser.add_argument("--file", type=Path)
    parser.add_argument("--note")
    parser.add_argument("--name")
    args = parser.parse_args()
    try:
        api = reference_api(args.threadtruth)
        if args.command == "prepare":
            if not args.spec:
                raise ValueError("prepare requires --spec")
            result = prepare(args.task, read(args.spec), api)
        elif args.command == "reserve":
            result = reserve(args.task, args.note, api)
        elif args.command == "returned":
            if not args.file:
                raise ValueError("returned requires --file")
            result = returned(args.task, args.file, api)
        elif args.command == "failed":
            result = failed(args.task, args.note, api)
        else:
            result = save(args.task, args.name, args.note, api)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, TypeError, KeyError, ledger.QuotaBlocked, ledger.LedgerMissing) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()
