"""Public-distribution checks; no live generation or private inputs."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/model-cast"


def test_public_example_asset_hashes_are_current():
    spec = SKILL / "references/pack-manifest.example.json"
    manifest = json.loads(spec.read_text())
    assets = [asset for group in ("originals", "motion", "identity_card")
              for asset in manifest[group].values()] + [manifest["diagram"]]
    for asset in assets:
        path = (spec.parent / asset["path"]).resolve()
        assert path.is_relative_to(ROOT / "tests/fixtures")
        assert hashlib.sha256(path.read_bytes()).hexdigest() == asset["sha256"], path.name
    for lang, asset in manifest["identity_card"].items():
        card = (spec.parent / asset["path"]).resolve()
        sheet = json.loads(Path(str(card) + ".sheet.json").read_text())
        assert sheet["output_sha256"] == asset["sha256"], lang
        for source in sheet["sources"]:
            assert hashlib.sha256((card.parent / source["path"]).read_bytes()).hexdigest() == source["sha256"]


def test_public_skill_is_self_contained_for_licensing_and_dependencies():
    assert (SKILL / "LICENSE").is_file()
    assert "MIT License" in (SKILL / "LICENSE").read_text()
    assert "Apache" in (SKILL / "vendor/lookset/LICENSE").read_text()
    assert (SKILL / "requirements.txt").is_file()
    assert "Pillow" in (SKILL / "requirements.txt").read_text()
    assert not (SKILL / "roster").exists()  # public seeds belong to the legacy main


def test_default_event_fixture_contains_no_plugin_contamination():
    path = ROOT / "tests/fixtures/t0-events-sample.jsonl"
    events = [json.loads(line) for line in path.read_text().splitlines()]
    assert events[0]["type"] == "thread.started"
    assert events[0]["thread_id"].startswith("synthetic-")
    for event in events:
        item = event.get("item", {})
        assert "/plugins/" not in item.get("command", "")
        assert len(item.get("aggregated_output", "")) < 200


def test_contaminated_event_fixture_is_explicitly_separate():
    path = ROOT / "tests/fixtures/synthetic-contaminated-events.jsonl"
    assert path.is_file()
    events = [json.loads(line) for line in path.read_text().splitlines()]
    assert events[0]["thread_id"].startswith("synthetic-")
    commands = [event.get("item", {}).get("command", "") for event in events]
    assert any("threadtruth-studio/" in c and "SKILL.md" in c for c in commands)
    assert path.stat().st_size < 2000
