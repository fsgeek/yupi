"""The training loop (trainer spec §2; plan Task 5) on a small real corpus
(C1 (8,4,2), generated into tmp_path by the corpus generator): the loss
falls, logs and the run manifest are written, and THE RESUME GATE — 20
straight steps vs 10 + checkpoint + fresh loop + 10 must give bit-identical
parameters on CPU (the lease memo of 2026-09-15). A resume with a different
config is refused."""
import json
from fractions import Fraction

import pytest

torch = pytest.importorskip("torch")

from yupi.corpus.manifest import Manifest, Split
from yupi.corpus.writer import generate
from yupi.learner.model import ModelConfig
from yupi.learner.train import TrainConfig, train


@pytest.fixture(scope="module")
def small_corpus(tmp_path_factory):
    root = tmp_path_factory.mktemp("corpus")
    m = Manifest.new(programs="c1", epsilon=Fraction(1), T_ep=8, L=4, B=2, rung="r4", run_key=b"\x01" * 32,
                     splits=(Split("train", 0, 512), Split("val", 1_000_000, 1_000_064), Split("test", 2_000_000, 2_000_064)),
                     git_commit="test")
    d, _ = generate(m, root, workers=2)
    return d


def _cfg(small_corpus, out, **kw):
    base = dict(corpus_dir=str(small_corpus), seed=1, out_dir=str(out), batch_size=64, epochs=4, warmup=5,   # 8 steps per epoch, 32 planned
                ckpt_every=10, val_every=10, model=ModelConfig(d_model=32, n_layer=1, n_head=2, d_mlp=64, n_pos=22))
    base.update(kw)
    return TrainConfig(**base)


def test_loss_falls_and_logs_parse(small_corpus, tmp_path):
    s = train(_cfg(small_corpus, tmp_path / "run", max_steps=30))
    log = [json.loads(l) for l in (tmp_path / "run" / "log.jsonl").read_text().splitlines()]
    assert s["step"] == 30 and log[-1]["step"] == 30 and log[-1]["val_loss"] < log[0]["val_loss"]
    run = json.loads((tmp_path / "run" / "run.json").read_text())
    assert run["seed"] == 1 and run["n_params"] == s["n_params"] and len(run["corpus_manifest_sha256"]) == 64
    assert (tmp_path / "run" / "ckpt.pt").exists()


def test_resume_gate_bit_identical_on_cpu(small_corpus, tmp_path):
    straight = train(_cfg(small_corpus, tmp_path / "a", max_steps=20))
    train(_cfg(small_corpus, tmp_path / "b", max_steps=10))
    resumed = train(_cfg(small_corpus, tmp_path / "b", max_steps=20), resume=True)
    pa = torch.load(tmp_path / "a" / "ckpt.pt", weights_only=False)["model"]
    pb = torch.load(tmp_path / "b" / "ckpt.pt", weights_only=False)["model"]
    assert set(pa) == set(pb) and all(torch.equal(pa[k], pb[k]) for k in pa)
    assert straight["step"] == resumed["step"] == 20 and straight["val_loss"] == resumed["val_loss"]


def test_resume_across_an_epoch_boundary_is_bit_identical(small_corpus, tmp_path):
    # 512 windows / 64 = 8 steps per epoch; 12 steps crosses into epoch 2
    train(_cfg(small_corpus, tmp_path / "a", epochs=2, max_steps=12, ckpt_every=100))
    train(_cfg(small_corpus, tmp_path / "b", epochs=2, max_steps=7, ckpt_every=100))
    train(_cfg(small_corpus, tmp_path / "b", epochs=2, max_steps=12, ckpt_every=100), resume=True)
    pa = torch.load(tmp_path / "a" / "ckpt.pt", weights_only=False)["model"]
    pb = torch.load(tmp_path / "b" / "ckpt.pt", weights_only=False)["model"]
    assert all(torch.equal(pa[k], pb[k]) for k in pa)


def test_resume_with_different_config_is_refused(small_corpus, tmp_path):
    train(_cfg(small_corpus, tmp_path / "c", max_steps=10))
    with pytest.raises(RuntimeError):
        train(_cfg(small_corpus, tmp_path / "c", max_steps=20, lr=5e-4), resume=True)


def test_cli_lr_min_defaults_to_a_tenth_of_lr_and_is_overridable():
    """The size-axis learning-rate sweep (note §11, §17.5) scales the cosine floor with
    the peak: --lr 3e-3 gives lr_min 3e-4 unless --lr-min is passed; the historical
    recipe (--lr 1e-3, no flag) still yields lr_min 1e-4."""
    import argparse, sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    import learner_train as lt
    ns = lambda **kw: argparse.Namespace(**{**dict(corpus_dir="c", seed=1, out="o", device="cpu", batch_size=256, epochs=5, lr=1e-3, lr_min=None,
                                                 warmup=500, ckpt_every=2000, val_every=1000, max_steps=None, d_model=128, n_layer=4, n_head=4), **kw})
    assert lt.build_config(ns()).lr_min == pytest.approx(1e-4)
    c = lt.build_config(ns(lr=3e-3, d_model=64))
    assert c.lr_min == pytest.approx(3e-4) and c.model.d_mlp == 256
    assert lt.build_config(ns(lr=3e-3, lr_min=5e-5)).lr_min == pytest.approx(5e-5)
