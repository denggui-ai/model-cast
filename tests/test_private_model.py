"""Offline behavior checks. Synthetic images/notes are not visual or user acceptance."""
import copy
import json
import os
from pathlib import Path

from PIL import Image
import pytest

import ledger
import private_model as pm


@pytest.fixture
def api():
    path = os.environ.get("MODEL_CAST_THREADTRUTH")
    if not path:
        pytest.skip("Set MODEL_CAST_THREADTRUTH to run the real consumer contract checks")
    return pm.reference_api(path)


@pytest.fixture
def spec():
    return {"model": {"source_type": "new", "scope": "face", "subject": "adult model",
                       "locked": ["short curly hair", "adult appearance"], "adjustable": [],
                       "styling_lock": "full", "consent_note": ""},
            "view": "face", "references": [], "source_note": "Synthetic offline test only"}


def fixture_image(path, color="green"):
    Image.new("RGB", (64, 96), color).save(path)
    return path


def test_new_candidate_to_real_consumer_package(tmp_path, api, spec, monkeypatch):
    public = tmp_path / "public"
    (public / "roster").mkdir(parents=True)
    index = public / "roster" / "index.json"
    index.write_text('{"keep":"public seed license unchanged"}')
    monkeypatch.setattr(pm, "ROOT", public)
    public_ledger = tmp_path / "public-ledger.json"
    ledger.init(public_ledger)
    monkeypatch.setenv("MODEL_CAST_LEDGER", str(public_ledger))
    before = public_ledger.read_bytes()
    task = tmp_path / "private"
    pm.prepare(task, spec, api)
    with pytest.raises(ValueError, match="text direction"):
        pm.save(task, "test", "synthetic test acceptance", api)
    request = pm.reserve(task, "synthetic one-call test authorization", api)
    assert "short curly hair" in request["image_gen_arguments"]["prompt"]
    assert "referenced_image_paths" not in request["image_gen_arguments"]
    with pytest.raises(ledger.QuotaBlocked):
        pm.reserve(task, "do not spend twice", api)
    image = fixture_image(tmp_path / "return.png")
    pm.returned(task, image, api)
    pm.returned(task, image, api)  # Recovery is idempotent, no new charge.
    pm.save(task, "Offline fixture", "Synthetic test acceptance; not a real user", api)
    card = api.load_package(task / "package")
    assert card["model"]["source_type"] == "ai"
    assert card["model"]["styling_lock"] == "full"
    assert card["references"][0]["sha256"] == api.digest(image)
    assert "license" not in card
    assert pm.read(task / "package" / "source.json")["automatic_license_grant"] is False
    assert ledger.remaining(task / "ledger.json") == {"roster_pool": 0, "shoot_pool": 0, "calls": 1}
    assert list((public / "roster").iterdir()) == [index]
    assert public_ledger.read_bytes() == before


def test_existing_ai_saves_without_generation_and_retains_source(tmp_path, api, spec):
    image = fixture_image(tmp_path / "ai.png")
    spec["model"]["source_type"] = "ai"
    spec["references"] = [str(image)]
    spec["source_note"] = "Existing test source; retain its original license, no exclusive rights"
    task = tmp_path / "existing"
    pm.prepare(task, spec, api)
    pm.save(task, "Existing AI", "Synthetic original-image acceptance", api)
    assert ledger.remaining(task / "ledger.json")["calls"] == 0
    assert pm.read(task / "package" / "source.json")["source_note"] == spec["source_note"]
    assert api.load_package(task / "package")["references"][0]["sha256"] == api.digest(image)
    with pytest.raises(ValueError, match="saved"):
        pm.reserve(task, "not authorized", api)
    with pytest.raises(ValueError, match="new package"):
        pm.save(task, "Overwrite", "test", api)


def test_existing_ai_variant_keeps_original_and_adds_accepted_supplement(tmp_path, api, spec):
    original = fixture_image(tmp_path / "original.png")
    spec["model"]["source_type"] = "ai"
    spec["references"] = [str(original)]
    spec["view"] = "full"
    task = tmp_path / "variant"
    pm.prepare(task, spec, api)
    request = pm.reserve(task, "Synthetic test", api)
    ref = Path(request["image_gen_arguments"]["referenced_image_paths"][0])
    assert ref.is_relative_to(task) and api.digest(ref) == api.digest(original)
    output = fixture_image(tmp_path / "variant.png", "blue")
    pm.returned(task, output, api)
    pm.save(task, "Variant", "Synthetic accepted body supplement", api)
    card = api.load_package(task / "package")
    assert card["model"]["scope"] == "face"
    assert card["references"][0]["sha256"] == api.digest(original)
    assert card["supplements"][0]["sha256"] == api.digest(output)
    assert card["supplements"][0]["scope"] == "full"


def test_fail_stop_and_recover_without_new_call(tmp_path, api, spec):
    task = tmp_path / "failed"
    pm.prepare(task, spec, api)
    pm.reserve(task, "Synthetic test", api)
    pm.failed(task, "Tool response unknown; no retry", api)
    before = (task / "ledger.json").read_bytes()
    with pytest.raises(FileExistsError):
        pm.prepare(task, spec, api)
    assert (task / "ledger.json").read_bytes() == before
    with pytest.raises(ledger.QuotaBlocked):
        pm.reserve(task, "No blind retry", api)
    with pytest.raises(ValueError, match="unresolved"):
        pm.save(task, "Bad", "Not accepted", api)
    pm.returned(task, fixture_image(tmp_path / "recovered.png"), api)
    assert (task / "failure.json").exists()
    assert ledger.remaining(task / "ledger.json")["calls"] == 1


def test_no_overwrite_or_changed_inputs(tmp_path, api, spec):
    task = tmp_path / "candidate"
    pm.prepare(task, spec, api)
    pm.reserve(task, "Synthetic test", api)
    image = fixture_image(tmp_path / "first.png")
    pm.returned(task, image, api)
    other = fixture_image(tmp_path / "other.png", "red")
    with pytest.raises(ValueError, match="replace"):
        pm.returned(task, other, api)
    (task / "task.json").write_text('{}')
    with pytest.raises(ValueError, match="changed"):
        pm.returned(task, image, api)


def test_no_public_task_even_through_symlink(tmp_path, api, spec, monkeypatch):
    public = tmp_path / "skill"
    public.mkdir()
    monkeypatch.setattr(pm, "ROOT", public)
    alias = tmp_path / "alias"
    alias.symlink_to(public, target_is_directory=True)
    with pytest.raises(ValueError, match="outside"):
        pm.prepare(alias / "roster" / "private", spec, api)
    assert list(public.iterdir()) == []


@pytest.mark.parametrize("change", [
    {"subject": "child model"}, {"source_type": "real"}, {"scope": "full"},
])
def test_reject_unsupported_scope_before_writing(tmp_path, api, spec, change):
    spec["model"].update(change)
    with pytest.raises(ValueError):
        pm.prepare(tmp_path / "bad", spec, api)
    assert not (tmp_path / "bad").exists()


def test_requires_explicit_styling_and_nonempty_acceptance(tmp_path, api, spec):
    invalid = copy.deepcopy(spec)
    del invalid["model"]["styling_lock"]
    with pytest.raises(ValueError, match="styling_lock"):
        pm.prepare(tmp_path / "bad", invalid, api)
    task = tmp_path / "good"
    pm.prepare(task, spec, api)
    with pytest.raises(ValueError):
        pm.reserve(task, "", api)
    assert ledger.remaining(task / "ledger.json")["calls"] == 0
    with pytest.raises(ValueError):
        pm.save(task, "No acceptance", "", api)


def test_reject_broken_image_and_preserve_reserved_call(tmp_path, api, spec):
    task = tmp_path / "decode"
    pm.prepare(task, spec, api)
    pm.reserve(task, "Synthetic test", api)
    image = tmp_path / "broken.png"
    image.write_text("not an image")
    with pytest.raises(ValueError):
        pm.returned(task, image, api)
    assert not (task / "output.json").exists()
    assert ledger.remaining(task / "ledger.json")["calls"] == 1


def test_private_budget_validation_and_public_defaults(tmp_path):
    for value in ({"roster_pool": -1, "shoot_pool": 0}, {"roster_pool": 1},
                  {"roster_pool": True, "shoot_pool": 0}):
        with pytest.raises(ValueError):
            ledger.init(tmp_path / "bad.json", budgets=value)
    assert not (tmp_path / "bad.json").exists()
    ledger.init(tmp_path / "public.json")
    assert ledger.remaining(tmp_path / "public.json") == {"roster_pool": 50, "shoot_pool": 4, "calls": 0}
