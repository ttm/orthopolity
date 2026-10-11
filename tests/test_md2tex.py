"""Check the small manuscript converter's supported Markdown constructs."""

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("manuscript_md2tex", ROOT / "tools" / "md2tex.py")
MD2TEX = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MD2TEX)


class ManuscriptConverterTests(unittest.TestCase):
    def test_prose_escape_does_not_escape_its_own_commands(self):
        self.assertEqual(
            MD2TEX.escape_text(r"a\b {c}_d & 10%"),
            r"a\textbackslash{}b \{c\}\_d \& 10\%",
        )

    def test_nested_inline_markup_keeps_math_and_code_intact(self):
        self.assertEqual(
            MD2TEX.inline(r"**`q_i`** and [$\bar q_i$](#cost), `$literal$`"),
            r"\textbf{\texttt{q\_i}} and \hyperlink{cost}{$\bar q_i$}, \texttt{\$literal\$}",
        )

    def test_only_manuscript_links_become_pdf_links(self):
        self.assertEqual(
            MD2TEX.inline("[Main](paper.md) [Proof](supporting-material.md#s1-proof) [Data](source.md#data)"),
            r"\href{paper.pdf}{Main} \href{supporting-material.pdf#nameddest=s1-proof}{Proof} \href{source.md#data}{Data}",
        )

    def test_contents_links_resolve_to_heading_anchors(self):
        md = """# Manuscript

- [S1. Accounting, composites and proofs](#s1-accounting-composites-and-proofs)

## S1. Accounting, composites and proofs

Some content.

## S1. Accounting, composites and proofs
"""
        tex = MD2TEX.convert(md, str(ROOT / "docs"), str(ROOT))
        self.assertIn(r"\hyperlink{s1-accounting-composites-and-proofs}", tex)
        self.assertIn(r"\hypertarget{s1-accounting-composites-and-proofs}{}", tex)
        self.assertIn(r"\hypertarget{s1-accounting-composites-and-proofs-1}{}", tex)

    def test_lists_preserve_item_boundaries_and_end_before_other_blocks(self):
        md = """# Manuscript

Paragraph before.
- First item
  continues here.
- Second with $q_i$.

3. Third item
4. Fourth item
## Next section

Paragraph after.
"""
        tex = MD2TEX.convert(md, str(ROOT / "docs"), str(ROOT))
        self.assertIn("\\begin{itemize}\n\\item First item continues here.\n\\item Second with $q_i$.\n\\end{itemize}", tex)
        self.assertIn("\\begin{enumerate}\n\\setcounter{enumi}{2}\n\\item Third item\n\\item Fourth item\n\\end{enumerate}", tex)
        self.assertLess(tex.index(r"\end{enumerate}"), tex.index(r"\section*{Next section}"))
        self.assertIn("Paragraph after.", tex)

    def test_actual_manuscript_contents_links_have_destinations(self):
        # Checks real document syntax without requiring a TeX installation.
        import re

        for source in ("paper.md", "supporting-material.md"):
            md = (ROOT / "docs" / source).read_text(encoding="utf-8")
            tex = MD2TEX.convert(md, str(ROOT / "docs"), str(ROOT))
            targets = set(re.findall(r"\\hypertarget\{([^}]+)\}", tex))
            self.assertFalse(set(re.findall(r"\\hyperlink\{([^}]+)\}", tex)) - targets)
            self.assertNotIn("\x00", tex)
            self.assertNotIn("ζ", tex)

    def test_table_caption_stays_inside_the_unbreakable_table_block(self):
        md = "# Paper\n\n| A | B |\n|---|---|\n| one | two |\n\n*Table 1. A caption\ncontinued here.*\n\nNext paragraph.\n"
        tex = MD2TEX.convert(md, str(ROOT/'docs'), str(ROOT))
        start = tex.index(r'\begin{minipage}')
        caption = tex.index('Table 1. A caption continued here.')
        end = tex.index(r'\end{minipage}')
        self.assertLess(start, caption)
        self.assertLess(caption, end)
        self.assertLess(end, tex.index('Next paragraph.'))
        self.assertEqual(tex.count('Table 1.'), 1)


if __name__ == "__main__":
    unittest.main()
