"""The learner's firewall (trainer spec §2): the training modules import
nothing from the exact side — the model must not be able to see the
ceiling, and only the evaluator may read it."""
import ast
import pathlib

SRC = pathlib.Path(__file__).parent.parent / "src" / "yupi" / "learner"
BANNED = ("yupi.naming", "yupi.pattern_", "yupi.window", "yupi.kernel", "yupi.enumerator", "yupi.filter",
          "yupi.predict", "yupi.forecast", "yupi.simulator", "yupi.queries", "yupi.state", "yupi.interfaces",
          "yupi.records", "yupi.programs", "yupi.config", "yupi.corpus.rendering", "yupi.corpus.windows")
ALLOWED = ("yupi.corpus.vocab", "yupi.corpus.writer", "yupi.corpus.manifest", "yupi.learner")


def _imports(p):
    tree = ast.parse(p.read_text())
    mods = [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    mods += [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
    return mods


def test_training_modules_cannot_see_the_exact_side():
    for name in ("data", "model", "train", "checkpoint"):
        for mod in _imports(SRC / f"{name}.py"):
            assert not any(mod.startswith(b) for b in BANNED), (name, mod)
            if mod.startswith("yupi"):
                assert any(mod.startswith(a) for a in ALLOWED), (name, mod)


def test_evaluator_is_the_only_module_that_reads_the_ceiling():
    mods = _imports(SRC / "evaluate.py")
    assert any(m.startswith("yupi.pattern_ceiling") for m in mods) and any(m.startswith("yupi.naming") for m in mods)
    assert not any(m.startswith("yupi.learner.train") for m in mods)     # the evaluator cannot train
