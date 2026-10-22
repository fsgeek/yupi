"""Build the methods paper in the TMLR format from docs/paper1m-manuscript-v2.md (owner, 2026-10-22).

Two variants:
  submission  anonymous (tmlr.sty without options), no contribution statement
  preprint    named ([preprint] option), with the contribution statement
  python scripts/build_tmlr.py STYLE_DIR      (STYLE_DIR holds tmlr.sty, tmlr.bst, fancyhdr.sty, math_commands.tex)
Outputs docs/tmlr/paper1m-{submission,preprint}.{tex,pdf}.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "paper1m-manuscript-v3.md"
OUT = ROOT / "docs" / "tmlr"
STYLE = Path(sys.argv[1])

UNICODE = {"§": r"\S{}", "½": r"\ensuremath{\tfrac{1}{2}}", "⅓": r"\ensuremath{\tfrac{1}{3}}", "×": r"\ensuremath{\times}",
           "Σ": r"\ensuremath{\Sigma}", "β": r"\ensuremath{\beta}", "δ": r"\ensuremath{\delta}", "ε": r"\ensuremath{\varepsilon}",
           "η": r"\ensuremath{\eta}", "ι": r"\ensuremath{\iota}", "–": "--", "—": "---", "‖": r"\ensuremath{\|}", "…": r"\ldots{}",
           "−": r"\ensuremath{-}", "≥": r"\ensuremath{\geq}", "¹": r"\textsuperscript{1}", "³": r"\textsuperscript{3}",
           "⁴": r"\textsuperscript{4}", "⁵": r"\textsuperscript{5}", "⁻": r"\textsuperscript{-}", "₂": r"\textsubscript{2}",
           "₄": r"\textsubscript{4}", "′": r"\ensuremath{'}", "⅔": r"\ensuremath{\tfrac{2}{3}}", "₁": r"\textsubscript{1}", "∈": r"\ensuremath{\in}", "λ": r"\ensuremath{\lambda}", "μ": r"\ensuremath{\mu}", "γ": r"\ensuremath{\gamma}", "α": r"\ensuremath{\alpha}", "≤": r"\ensuremath{\leq}"}


def section(md, heading):
    m = re.search(rf"^## {re.escape(heading)}.*$", md, re.M)
    rest = md[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    return rest[:nxt.start() if nxt else len(rest)].strip()


def to_latex(md):
    md = md.replace("q̃", r"$\tilde{q}$")
    r = subprocess.run(["pandoc", "-f", "markdown", "-t", "latex", "--natbib", "--wrap=preserve", "--shift-heading-level-by=-1"],
                       input=md, capture_output=True, text=True, check=True)
    tex = r.stdout
    return tex


def strip_numbers(tex):
    # Markdown headings carry their own numbers ("## 3. What …"); let LaTeX number them.
    return re.sub(r"\\(section|subsection)\{(?:Appendix A\.\s*)?\d+(?:\.\d+)?\.?\s+", r"\\\1{", tex)


def build(variant):
    md = SRC.read_text()
    md = md[md.index("\n---\n", 4) + 5:]  # drop YAML header
    if variant == "submission":   # double-blind: the kernel's name leads to a public repository
        md = md.replace("**The world.** Yupana is", "**The world.** Our world is")
        md = md.replace("Yupana is a small stochastic operating-system kernel", "The world is a small stochastic operating-system kernel")
        assert "Yupana" not in md, "kernel name left in submission"
    title = "An exact world audits its own experiments: what a small stochastic kernel can and cannot settle about learners"
    abstract = section(md, "Abstract")
    body_md = md[md.index("## 1. Introduction"):md.index("## Contribution statement")]
    contrib = section(md, "Contribution statement")
    appendix = md[md.index("## Appendix A"):]
    appendix = appendix.replace("## Appendix A. Which models carry which claim", "## Which models carry which claim")
    appendix = appendix.replace("## Appendix B. The kernel and the exact computation", "## The kernel and the exact computation")
    body = strip_numbers(to_latex(body_md))
    app = strip_numbers(to_latex(appendix))
    if variant == "submission":
        contrib_tex = ("\\section*{Disclosure}\nThe research and the writing were conducted largely by AI agents (large "
                       "language models) under human direction, with adversarial review of designs, pre-registrations and "
                       "results by separate AI agents. A full contribution statement appears in the de-anonymised version.\n")
    else:
        contrib_tex = "\\section*{Contribution statement}\n" + to_latex(contrib)
    opt = "" if variant == "submission" else "[preprint]"
    author_line = ("\\author{\\name Anonymous authors}" if variant == "submission" else
                   "\\author{\\name W. Anthony Mason \\email fsgeek@cs.ubc.ca \\\\ \\addr University of British Columbia}")
    decls = "\n".join(f"\\DeclareUnicodeCharacter{{{ord(c):04X}}}{{{v}}}" for c, v in UNICODE.items())
    tex = f"""\\documentclass[10pt]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{opt}{{tmlr}}
\\usepackage{{hyperref}}
\\usepackage{{url}}
\\usepackage{{amsmath,amssymb}}
\\usepackage{{longtable,booktabs,array,calc}}
\\providecommand{{\\tightlist}}{{\\setlength{{\\itemsep}}{{0pt}}\\setlength{{\\parskip}}{{0pt}}}}
\\providecommand{{\\pandocbounded}}[1]{{#1}}
{decls}
\\title{{{title}}}
{author_line}
\\def\\month{{MM}}
\\def\\year{{YYYY}}
\\def\\openreview{{\\url{{https://openreview.net/forum?id=XXXX}}}}
\\begin{{document}}
\\maketitle
\\begin{{abstract}}
{to_latex(abstract)}
\\end{{abstract}}
{body}
{contrib_tex}
\\bibliography{{paper1m}}
\\bibliographystyle{{tmlr}}
\\appendix
{app}
\\end{{document}}
"""
    work = OUT / f"build-{variant}"
    work.mkdir(parents=True, exist_ok=True)
    for f in ("tmlr.sty", "tmlr.bst", "fancyhdr.sty", "math_commands.tex"):
        shutil.copy(STYLE / f, work / f)
    shutil.copy(OUT / "paper1m.bib", work / "paper1m.bib")
    (work / f"paper1m-{variant}.tex").write_text(tex)
    for cmd in (["pdflatex", "-interaction=nonstopmode", f"paper1m-{variant}.tex"], ["bibtex", f"paper1m-{variant}"],
                ["pdflatex", "-interaction=nonstopmode", f"paper1m-{variant}.tex"],
                ["pdflatex", "-interaction=nonstopmode", f"paper1m-{variant}.tex"]):
        subprocess.run(cmd, cwd=work, capture_output=True, text=True, errors="replace")
    pdf = work / f"paper1m-{variant}.pdf"
    log = (work / f"paper1m-{variant}.log").read_text(errors="ignore")
    errs = [l for l in log.splitlines() if l.startswith("!")]
    undef = sorted(set(re.findall(r"Citation `([^']+)' .*undefined", log)))
    shutil.copy(work / f"paper1m-{variant}.tex", OUT / f"paper1m-{variant}.tex")
    if pdf.exists():
        shutil.copy(pdf, OUT / f"paper1m-{variant}.pdf")
    print(variant, "pdf" if pdf.exists() else "NO PDF", "| errors:", errs[:5] or "none", "| undefined citations:", undef or "none")


for v in ("submission", "preprint"):
    build(v)
