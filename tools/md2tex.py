"""Convert the manuscript Markdown into LaTeX for a print-ready PDF.

The manuscript uses a narrow Markdown subset -- headings, paragraphs, inline and
display math, two pipe tables, one figure, links and a leading note block -- so a
small dedicated converter avoids adding a Pandoc dependency to the reproduce path.

    python3 tools/md2tex.py docs/paper.md build/paper.tex

Image paths are rewritten relative to the repository root, which is where the
Makefile runs pdflatex from.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage[margin=2.5cm]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage[font=small]{caption}
\usepackage{textcomp}
\usepackage[hidelinks,breaklinks]{hyperref}
\usepackage{microtype}

% Byte-reproducible output: a fixed trailer id, with document timestamps coming
% from SOURCE_DATE_EPOCH, so rebuilding an unchanged manuscript changes nothing.
\ifdefined\pdfvariable\pdfvariable trailerid{}\fi

\setlength{\parskip}{0.4em}
\setlength{\parindent}{0pt}
\renewcommand{\arraystretch}{1.25}

% Hanging indent for the reference list.
\newenvironment{referencelist}%
  {\small\setlength{\parskip}{0.5em}\setlength{\leftskip}{1.5em}\setlength{\parindent}{-1.5em}}%
  {\par}

% A quiet block for the manuscript status note under the title.
\newenvironment{statusnote}%
  {\begin{quote}\small\itshape}%
  {\end{quote}}

\title{@@TITLE@@}
\author{}
\date{}
"""

TEXT_SPECIALS = [
    ("\\", r"\textbackslash{}"),
    ("{", r"\{"),
    ("}", r"\}"),
    ("&", r"\&"),
    ("%", r"\%"),
    ("$", r"\$"),
    ("#", r"\#"),
    ("_", r"\_"),
    ("~", r"\textasciitilde{}"),
    ("^", r"\textasciicircum{}"),
]

UNICODE_TEXT = [
    ("\u2014", r"\textemdash{}"),
    ("\u2013", r"\textendash{}"),
    ("\u2212", r"$-$"),
    ("\u00b2", r"\textsuperscript{2}"),
    ("\u00a7", r"\S{}"),
    ("\u201c", r"``"),
    ("\u201d", r"''"),
    ("\u2019", r"'"),
    ("\u2018", r"`"),
    ("\u00d7", r"$\times$"),
    ("\u00b0", r"\textdegree{}"),
    ("\u00a0", "~"),
]

UNICODE_MATH = [
    ("\u2212", "-"),
    ("\u2013", "-"),
    ("\u00d7", r"\times "),
    ("\u00a0", " "),
]

SENTINEL = "\x00"


def escape_text(text: str) -> str:
    """Escape LaTeX specials in ordinary prose, then map the Unicode we use."""
    for src, dst in TEXT_SPECIALS:
        text = text.replace(src, dst)
    for src, dst in UNICODE_TEXT:
        text = text.replace(src, dst)
    return text


def fix_math(text: str) -> str:
    for src, dst in UNICODE_MATH:
        text = text.replace(src, dst)
    return text


def inline(text: str) -> str:
    """Convert one run of Markdown prose, protecting math and links from escaping."""
    protected: list[str] = []

    def stash(latex: str) -> str:
        protected.append(latex)
        return f"{SENTINEL}{len(protected) - 1}{SENTINEL}"

    # Inline math first: its content must reach LaTeX unescaped.
    text = re.sub(r"\$([^$]+)\$", lambda m: stash("$" + fix_math(m.group(1)) + "$"), text)
    # Autolinks <https://...>.
    text = re.sub(r"<((?:https?|mailto):[^>]+)>", lambda m: stash(r"\url{" + m.group(1) + "}"), text)
    # Inline links [text](target); the label still needs escaping, the target does not.
    text = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: stash(r"\href{" + m.group(2) + "}{" + inline(m.group(1)) + "}"),
        text,
    )

    text = escape_text(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text, flags=re.S)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\\emph{\1}", text, flags=re.S)

    return re.sub(
        rf"{SENTINEL}(\d+){SENTINEL}", lambda m: protected[int(m.group(1))], text
    )


def heading(level: int, text: str, out: list[str]) -> None:
    """Sections are numbered in the source, so emit starred ones plus a bookmark."""
    cmd = {2: "section", 3: "subsection", 4: "subsubsection"}[level]
    body = inline(text)
    out.append(rf"\phantomsection\addcontentsline{{toc}}{{{cmd}}}{{{body}}}")
    out.append(rf"\{cmd}*{{{body}}}")


def emit_table(rows: list[str], out: list[str]) -> None:
    cells = [[c.strip() for c in row.strip().strip("|").split("|")] for row in rows]
    header, body = cells[0], cells[2:]  # cells[1] is the alignment rule
    spec = "".join("X" for _ in header)
    out.append(r"\begin{center}\small")
    out.append(rf"\begin{{tabularx}}{{\linewidth}}{{@{{}}{spec}@{{}}}}")
    out.append(r"\toprule")
    out.append(" & ".join(rf"\textbf{{{inline(c)}}}" for c in header) + r" \\")
    out.append(r"\midrule")
    for row in body:
        row = row + [""] * (len(header) - len(row))
        out.append(" & ".join(inline(c) for c in row[: len(header)]) + r" \\")
    out.append(r"\bottomrule")
    out.append(r"\end{tabularx}")
    out.append(r"\end{center}")


def convert(md: str, md_dir: str, root: str) -> str:
    lines = md.split("\n")
    out: list[str] = []
    title = ""
    subtitle = ""
    body_started = False
    section = ""
    in_abstract = False
    in_references = False
    pending_figure: str | None = None

    def close_environments() -> None:
        nonlocal in_abstract, in_references
        if in_abstract:
            out.append(r"\end{abstract}")
            in_abstract = False
        if in_references:
            out.append(r"\end{referencelist}")
            in_references = False

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # Title and the bold subtitle that follows it.
        if stripped.startswith("# ") and not title:
            title = inline(stripped[2:].strip())
            i += 1
            continue
        if not body_started and re.fullmatch(r"\*\*.+\*\*", stripped) and not subtitle:
            subtitle = inline(stripped[2:-2].strip())
            i += 1
            continue

        # Status note: the blockquote under the title.
        if stripped.startswith(">"):
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            if not body_started:
                out.append(r"\begin{statusnote}")
                out.append(inline(" ".join(quote)))
                out.append(r"\end{statusnote}")
                body_started = True
            else:
                out.append(r"\begin{quote}\small")
                out.append(inline(" ".join(quote)))
                out.append(r"\end{quote}")
            continue

        # Headings.
        m = re.match(r"^(#{2,4})\s+(.*)$", stripped)
        if m:
            level, text = len(m.group(1)), m.group(2).strip()
            close_environments()
            body_started = True
            section = text.lower()
            if section == "abstract":
                out.append(r"\begin{abstract}")
                in_abstract = True
            else:
                heading(level, text, out)
                if section == "references":
                    out.append(r"\begin{referencelist}")
                    in_references = True
            i += 1
            continue

        # Display math, possibly spanning several lines.
        if stripped.startswith("$$"):
            chunk = [stripped]
            if not (stripped.endswith("$$") and len(stripped) > 2):
                i += 1
                while i < len(lines) and not lines[i].strip().endswith("$$"):
                    chunk.append(lines[i].strip())
                    i += 1
                if i < len(lines):
                    chunk.append(lines[i].strip())
            body = " ".join(chunk).strip()
            body = fix_math(body[2:-2].strip())
            out.append(r"\begin{equation*}")
            out.append(body)
            out.append(r"\end{equation*}")
            i += 1
            continue

        # Pipe tables.
        if stripped.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            if len(rows) >= 2:
                emit_table(rows, out)
            continue

        # Figures: the image line, with the following italic paragraph as caption.
        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", stripped)
        if m:
            path = m.group(2)
            if not path.startswith(("http://", "https://", "/")):
                path = os.path.relpath(os.path.join(md_dir, path), root)
            pending_figure = path
            i += 1
            continue

        # Ordinary paragraph: gather until a blank line or a block marker.
        para = []
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt or nxt.startswith(("#", "|", "$$", ">", "![")):
                break
            para.append(nxt)
            i += 1
        text = " ".join(para)

        if pending_figure is not None:
            out.append(r"\begin{figure}[htbp]")
            out.append(r"\centering")
            out.append(rf"\includegraphics[width=\linewidth]{{{pending_figure}}}")
            if text.startswith("*") and text.endswith("*"):
                out.append(rf"\caption*{{{inline(text[1:-1])}}}")
                text = ""
            out.append(r"\end{figure}")
            pending_figure = None

        if text:
            out.append(inline(text))
            out.append("")

    close_environments()

    preamble = PREAMBLE.replace("@@TITLE@@", title)
    head = [preamble, r"\begin{document}"]
    if subtitle:
        head.append(
            r"\maketitle" + "\n" + r"\vspace{-3.5em}" + "\n"
            r"\begin{center}\large " + subtitle + r"\end{center}" + "\n" + r"\vspace{1.5em}"
        )
    else:
        head.append(r"\maketitle")
    return "\n".join(head + out + [r"\end{document}", ""])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", help="Markdown manuscript")
    ap.add_argument("target", help="LaTeX file to write")
    ap.add_argument(
        "--root",
        default=os.getcwd(),
        help="directory pdflatex will run from; image paths are made relative to it",
    )
    args = ap.parse_args()

    with open(args.source, encoding="utf-8") as fh:
        md = fh.read()

    tex = convert(md, os.path.dirname(os.path.abspath(args.source)), os.path.abspath(args.root))
    os.makedirs(os.path.dirname(os.path.abspath(args.target)), exist_ok=True)
    with open(args.target, "w", encoding="utf-8") as fh:
        fh.write(tex)
    return 0


if __name__ == "__main__":
    sys.exit(main())
