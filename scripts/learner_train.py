"""Train one model on one corpus (trainer spec; plan Task 5).

  uv run --extra learner python scripts/learner_train.py --corpus-dir corpus/<name>/<run-id> --seed 1 \\
      --out ~/.cache/yupi-scratch/runs/<cell>-s1 [--device cpu|cuda] [--epochs 10] [--batch-size 256] \\
      [--max-steps N] [--resume]

Prints the summary JSON. SIGTERM (the lease's kill) checkpoints and exits 0;
rerun with --resume to continue from the checkpoint.
"""
import argparse
import json
import sys

from yupi.learner.model import ModelConfig
from yupi.learner.train import TrainConfig, train


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus-dir", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--batch-size", type=int, default=256)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--warmup", type=int, default=500)
    ap.add_argument("--ckpt-every", type=int, default=500)
    ap.add_argument("--val-every", type=int, default=250)
    ap.add_argument("--max-steps", type=int, default=None)
    ap.add_argument("--d-model", type=int, default=128)
    ap.add_argument("--n-layer", type=int, default=4)
    ap.add_argument("--n-head", type=int, default=4)
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args(argv)
    model = ModelConfig(d_model=a.d_model, n_layer=a.n_layer, n_head=a.n_head, d_mlp=4 * a.d_model)
    cfg = TrainConfig(corpus_dir=a.corpus_dir, seed=a.seed, out_dir=a.out, device=a.device, batch_size=a.batch_size,
                      epochs=a.epochs, lr=a.lr, warmup=a.warmup, ckpt_every=a.ckpt_every, val_every=a.val_every,
                      max_steps=a.max_steps, model=model)
    print(json.dumps(train(cfg, resume=a.resume), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
