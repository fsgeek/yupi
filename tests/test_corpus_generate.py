"""The CLI writes a corpus and a committed-manifest copy; regenerating from
that copy is byte-identical (design gate 1)."""
import filecmp
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import corpus_generate as G  # noqa: E402


def test_cli_new_run_then_regenerate_from_manifest(tmp_path):
    root, copies = tmp_path / "corpus", tmp_path / "manifests"
    rc = G.main(["--programs", "c1", "--law", "8", "4", "2", "--rung", "r2", "--eps", "1",
                 "--train", "50", "--val", "5", "--test", "5", "--workers", "2",
                 "--root", str(root), "--run-key", "00" * 32, "--manifest-copy", str(copies)])
    assert rc == 0
    (copy,) = list(copies.glob("*.json"))
    m = json.loads(copy.read_text())
    assert m["counts"] == {"train": 50, "val": 5, "test": 5} and m["rung"] == "r2"
    d = next((root / "c1-8-4-2-r2-eps1").iterdir())          # the single run directory
    root2 = tmp_path / "corpus2"
    assert G.main(["--from-manifest", str(copy), "--root", str(root2), "--workers", "1",
                   "--manifest-copy", str(tmp_path / "manifests2")]) == 0
    d2 = next((root2 / "c1-8-4-2-r2-eps1").iterdir())
    for name in ("train.tokens", "train.index", "train.table.jsonl", "test.tokens", "manifest.json"):
        assert filecmp.cmp(d / name, d2 / name, shallow=False), name


def test_default_splits_are_disjoint_and_named():
    s = G.default_splits(200_000, 10_000, 10_000)
    assert [x.name for x in s] == ["train", "val", "test"]
    assert (s[0].seed_start, s[0].seed_end) == (0, 200_000)
    assert (s[1].seed_start, s[1].seed_end) == (1_000_000, 1_010_000)
    assert (s[2].seed_start, s[2].seed_end) == (2_000_000, 2_010_000)
