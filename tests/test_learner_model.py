"""The decoder (trainer spec §2; plan Task 3): written out in full so the
residual stream is reachable per layer. Causality, shapes, the parameter
count against the arithmetic, and determinism of the forward pass."""
import pytest

torch = pytest.importorskip("torch")

from yupi.learner.model import Decoder, ModelConfig, n_params


def test_causal_and_shapes():
    torch.manual_seed(0)
    m = Decoder(ModelConfig()).eval()
    x = torch.randint(0, 157, (3, 42))
    with torch.no_grad():
        a, hs = m(x, return_hidden=True)
        x2 = x.clone()
        x2[:, 20] = (x2[:, 20] + 1) % 157
        b = m(x2)
    assert a.shape == (3, 42, 156)
    assert len(hs) == 5 and all(h.shape == (3, 42, 128) for h in hs)       # embeddings + after each of 4 blocks
    assert torch.allclose(a[:, :20], b[:, :20], atol=1e-6) and not torch.allclose(a[:, 20:], b[:, 20:])


def test_param_count_matches_arithmetic():
    cfg = ModelConfig()
    d, L, f = cfg.d_model, cfg.n_layer, cfg.d_mlp
    per_block = (3 * d * d + 3 * d) + (d * d + d) + (2 * d * f + f + d) + 2 * (2 * d)   # qkv, o, mlp, two LayerNorms
    expect = cfg.vocab_in * d + cfg.n_pos * d + L * per_block + 2 * d + (d * cfg.vocab_out + cfg.vocab_out)
    got = n_params(Decoder(cfg))
    assert got == expect and 0.8e6 < got < 0.9e6, (got, expect)


def test_forward_is_deterministic_on_cpu():
    torch.manual_seed(1)
    m = Decoder(ModelConfig(d_model=32, n_layer=2, n_head=2, d_mlp=64, n_pos=22)).eval()
    x = torch.randint(0, 157, (4, 22))
    with torch.no_grad():
        assert torch.equal(m(x), m(x))


def test_small_config_shapes():
    m = Decoder(ModelConfig(d_model=32, n_layer=1, n_head=2, d_mlp=64, n_pos=22))
    out, hs = m(torch.zeros(2, 22, dtype=torch.long), return_hidden=True)
    assert out.shape == (2, 22, 156) and len(hs) == 2


def test_gru_baseline_shape_causality_and_factory():
    # 2026-10-13: the recurrent baseline (whole-draft review W28). Same input/output contract as Decoder; causal by
    # construction; build_model dispatches on arch, defaulting to the transformer so old configs load unchanged.
    import torch
    from yupi.learner.model import GRUNet, build_model, n_params
    c = ModelConfig(arch="gru", d_model=32, n_layer=2, n_pos=22)
    m = build_model(c).eval()
    assert isinstance(m, GRUNet)
    x = torch.randint(0, 157, (3, 20))
    y = m(x)
    assert y.shape == (3, 20, 156)
    x2 = x.clone(); x2[:, 15:] = (x2[:, 15:] + 1) % 157
    assert torch.allclose(m(x2)[:, :15], y[:, :15])            # positions before 15 never see later inputs
    assert isinstance(build_model(ModelConfig()), Decoder)
    assert ModelConfig(**{k: v for k, v in ModelConfig().__dict__.items() if k != "arch"}).arch == "transformer"
    full = build_model(ModelConfig(arch="gru", d_model=256, n_layer=2))
    assert 800_000 < n_params(full) < 950_000                   # matched to the transformer's 838,940
