"""GPU determinism check for the trainer (spec §2 'Precision'; the lease memo: any GPU difference is
measured, not hidden). Two identical 60-step runs on cuda; and the resume gate on cuda (30 + 30 vs 60)."""
import json, sys, tempfile
from fractions import Fraction
from pathlib import Path
import torch
from yupi.corpus.manifest import Manifest, Split
from yupi.corpus.writer import generate
from yupi.learner.model import ModelConfig
from yupi.learner.train import TrainConfig, train

root = Path(tempfile.mkdtemp(prefix="yupi-gpu-"))
m = Manifest.new(programs="c1", epsilon=Fraction(1), T_ep=8, L=4, B=2, rung="r4", run_key=b"\x05" * 32,
                 splits=(Split("train", 0, 2048), Split("val", 1_000_000, 1_000_128), Split("test", 2_000_000, 2_000_128)), git_commit="gpu-check")
d, _ = generate(m, root, workers=1)
def cfg(out, steps):
    return TrainConfig(corpus_dir=str(d), seed=11, out_dir=str(out), device="cuda", batch_size=64, epochs=4, warmup=5,
                       ckpt_every=30, val_every=30, max_steps=steps, model=ModelConfig(n_pos=22))
def params(out):
    return torch.load(Path(out) / "ckpt.pt", weights_only=False)["model"]
def maxdiff(a, b):
    return max(float((a[k].double() - b[k].double()).abs().max()) for k in a)
train(cfg(root / "a", 60)); train(cfg(root / "b", 60))
train(cfg(root / "c", 30)); train(cfg(root / "c", 60), resume=True)
pa, pb, pc = params(root / "a"), params(root / "b"), params(root / "c")
out = dict(device=torch.cuda.get_device_name(0), torch=torch.__version__, repeat_max_abs_diff=maxdiff(pa, pb),
           resume_max_abs_diff=maxdiff(pa, pc), bit_identical_repeat=all(torch.equal(pa[k], pb[k]) for k in pa),
           bit_identical_resume=all(torch.equal(pa[k], pc[k]) for k in pa))
print(json.dumps(out, indent=2))
Path(sys.argv[1]).write_text(json.dumps(out, indent=2) + "\n")
