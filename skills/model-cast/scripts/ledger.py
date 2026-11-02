#!/usr/bin/env python3
"""Codex call ledger with two budget pools. Every Codex image call must reserve first.

Pools are spent on reserve (success, failure and 429 all count); an empty pool raises
QuotaBlocked and never overspends. All writes happen under an exclusive file lock.
"""
import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULTS = {"roster_pool": 50, "shoot_pool": 4}


class QuotaBlocked(RuntimeError):
    pass


class LedgerMissing(RuntimeError):
    """The ledger file does not exist; it must be created explicitly with `ledger.py --init`."""


def home():
    """Repo root that owns state/: MODEL_CAST_HOME, else the main worktree (git common dir), else this repo."""
    if os.environ.get("MODEL_CAST_HOME"):
        return Path(os.environ["MODEL_CAST_HOME"]).expanduser().resolve()
    try:
        common = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--git-common-dir"], capture_output=True,
                                text=True, check=True).stdout.strip()
        return (ROOT / common).resolve().parent
    except (OSError, subprocess.CalledProcessError):
        return ROOT


def default_path():
    return Path(os.environ.get("MODEL_CAST_LEDGER") or home() / "state" / "ledger.json")


@contextmanager
def _locked(path, create=False):
    path = Path(path) if path else default_path()
    if not create and not path.exists():
        raise LedgerMissing(f"ledger not found: {path} (create it once with: ledger.py --init)")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path.with_name(path.name + ".lock"), "a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if not create and not path.exists():  # deleted between the pre-check and taking the lock
            raise LedgerMissing(f"ledger not found: {path} (create it once with: ledger.py --init)")
        if create:
            if path.exists():
                raise FileExistsError(f"ledger already exists: {path}")
            data = {**DEFAULTS, "calls": []}
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
        yield data
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, path)


def reserve(pool, purpose, model_id, step, path=None):
    if pool not in DEFAULTS:
        raise ValueError(f"unknown pool: {pool}")
    with _locked(path) as d:
        if d[pool] <= 0:
            raise QuotaBlocked(f"{pool} is empty; ask the Owner to add budget")
        d[pool] -= 1
        n = len(d["calls"]) + 1
        d["calls"].append({"n": n, "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "purpose": purpose,
                           "model_id": model_id, "step": step, "pool": pool, "status": "reserved",
                           "thread_id": None, "image_path": None})
        return n


def record(n, status, thread_id=None, image_path=None, path=None):
    with _locked(path) as d:
        d["calls"][n - 1].update(status=status, thread_id=thread_id, image_path=image_path)


def remaining(path=None):
    with _locked(path) as d:
        return {"roster_pool": d["roster_pool"], "shoot_pool": d["shoot_pool"], "calls": len(d["calls"])}


def add_pool(pool, n, path=None):
    if pool not in DEFAULTS:
        raise ValueError(f"unknown pool: {pool}")
    with _locked(path) as d:
        d[pool] += n


def model_calls(model_id, path=None):
    """Number of charged calls for a model (reserved and not refunded). Raises LedgerMissing if no ledger."""
    with _locked(path) as d:
        return sum(1 for c in d["calls"] if c["model_id"] == model_id and not c.get("refunded"))


def init(path=None, *, budgets=None):
    """Create a fresh ledger; optional exact pools support isolated private tasks."""
    if budgets is not None:
        if (set(budgets) != set(DEFAULTS)
                or any(type(n) is not int or n < 0 for n in budgets.values())):
            raise ValueError("budgets must declare both pools with nonnegative integer values")
    with _locked(path, create=True) as data:
        if budgets is not None:
            data.update(budgets)


def refund(n, status, path=None):
    """Give back the point of call n (Codex was never invoked). Idempotent."""
    with _locked(path) as d:
        call = d["calls"][n - 1]
        if not call.get("refunded"):
            d[call["pool"]] += 1
            call["refunded"] = True
        call["status"] = status


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--init", action="store_true", help="create state/ledger.json (refuses if it exists)")
    ap.add_argument("--show", action="store_true", help="print remaining pools")
    args = ap.parse_args()
    try:
        if args.init:
            init()
            print(f"created {default_path()}")
        else:
            print(json.dumps(remaining(), ensure_ascii=False))
    except (FileExistsError, LedgerMissing) as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
