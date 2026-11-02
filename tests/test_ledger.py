import json
import multiprocessing as mp

import pytest

import ledger


def _mk(tmp_path):
    p = tmp_path / "l.json"
    ledger.init(p)
    return p


def test_initial_defaults(tmp_path):
    p = _mk(tmp_path)
    assert ledger.remaining(p) == {"roster_pool": 50, "shoot_pool": 4, "calls": 0}


def test_reserve_deducts_and_numbers(tmp_path):
    p = _mk(tmp_path)
    assert ledger.reserve("roster_pool", "roster", "mc-001", "face", p) == 1
    assert ledger.reserve("roster_pool", "roster", "mc-001", "three_quarter", p) == 2
    assert ledger.remaining(p) == {"roster_pool": 48, "shoot_pool": 4, "calls": 2}


def test_pool_empty_raises_and_writes_nothing(tmp_path):
    p = _mk(tmp_path)
    for _ in range(4):
        ledger.reserve("shoot_pool", "shoot", "mc-001", "shot", p)
    before = ledger.remaining(p)
    with pytest.raises(ledger.QuotaBlocked):
        ledger.reserve("shoot_pool", "shoot", "mc-001", "shot", p)
    assert ledger.remaining(p) == before == {"roster_pool": 50, "shoot_pool": 0, "calls": 4}


def test_bad_pool_name(tmp_path):
    with pytest.raises(ValueError):
        ledger.reserve("nope", "roster", "mc-001", "face", tmp_path / "l.json")


def test_failure_still_counts(tmp_path):
    p = _mk(tmp_path)
    n = ledger.reserve("roster_pool", "roster", "mc-001", "face", p)
    ledger.record(n, "rate_limited", thread_id="t1", path=p)
    assert ledger.remaining(p)["roster_pool"] == 49
    call = json.loads(p.read_text())["calls"][0]
    assert call["status"] == "rate_limited" and call["thread_id"] == "t1"


def test_add_pool(tmp_path):
    p = _mk(tmp_path)
    ledger.add_pool("roster_pool", 6, p)
    assert ledger.remaining(p)["roster_pool"] == 56


def _worker(path, out):
    try:
        ledger.reserve("shoot_pool", "shoot", "mc-001", "shot", path)
        out.put("ok")
    except ledger.QuotaBlocked:
        out.put("blocked")


def test_concurrent_reserve_never_overspends(tmp_path):
    p = _mk(tmp_path)
    q = mp.Queue()
    procs = [mp.Process(target=_worker, args=(p, q)) for _ in range(8)]
    [x.start() for x in procs]
    [x.join() for x in procs]
    results = [q.get() for _ in procs]
    assert results.count("ok") == 4 and results.count("blocked") == 4
    assert ledger.remaining(p)["shoot_pool"] == 0


def test_missing_ledger_raises_and_creates_nothing(tmp_path):
    p = tmp_path / "state" / "l.json"
    with pytest.raises(ledger.LedgerMissing):
        ledger.reserve("roster_pool", "roster", "mc-001", "face", p)
    with pytest.raises(ledger.LedgerMissing):
        ledger.remaining(p)
    assert not p.exists() and not p.parent.exists()


def test_init_twice_fails(tmp_path):
    p = tmp_path / "l.json"
    ledger.init(p)
    with pytest.raises(FileExistsError):
        ledger.init(p)
    assert ledger.remaining(p)["roster_pool"] == 50


def test_refund_is_idempotent_and_returns_point(tmp_path):
    p = _mk(tmp_path)
    n = ledger.reserve("roster_pool", "roster", "mc-001", "face", p)
    ledger.refund(n, "busy", p)
    ledger.refund(n, "busy", p)
    assert ledger.remaining(p)["roster_pool"] == 50
    assert json.loads(p.read_text())["calls"][0]["status"] == "busy"


def test_worktree_resolves_to_main_repo(tmp_path, monkeypatch):
    import subprocess
    monkeypatch.delenv("MODEL_CAST_HOME", raising=False)
    monkeypatch.delenv("MODEL_CAST_LEDGER", raising=False)
    main = tmp_path / "main"
    (main / "scripts").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(main)], check=True)
    subprocess.run(["git", "-C", str(main), "-c", "user.name=t", "-c", "user.email=t" + "@" + "t.t", "commit", "-q",
                    "--allow-empty", "-m", "x"], check=True)
    wt = tmp_path / "wt"
    subprocess.run(["git", "-C", str(main), "worktree", "add", "-q", str(wt), "-b", "b"], check=True)
    (wt / "scripts").mkdir(exist_ok=True)
    monkeypatch.setattr(ledger, "ROOT", wt)
    assert ledger.default_path() == main.resolve() / "state" / "ledger.json"


def test_model_cast_home_wins(tmp_path, monkeypatch):
    monkeypatch.delenv("MODEL_CAST_LEDGER", raising=False)
    monkeypatch.setenv("MODEL_CAST_HOME", str(tmp_path))
    assert ledger.default_path() == tmp_path.resolve() / "state" / "ledger.json"


def test_ledger_deleted_between_check_and_lock_is_reported_not_crash(tmp_path, monkeypatch):
    p = _mk(tmp_path)
    real_exists = type(p).exists
    calls = {"n": 0}

    def flaky(self):  # first call (pre-lock check) says yes, then the file vanishes
        if self == p:
            calls["n"] += 1
            if calls["n"] == 1:
                p.unlink()
                return True
        return real_exists(self)
    monkeypatch.setattr(type(p), "exists", flaky)
    with pytest.raises(ledger.LedgerMissing):
        ledger.reserve("roster_pool", "roster", "mc-001", "face", p)
