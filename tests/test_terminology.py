import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# The adjective is "orthopolic" (docs/glossary.md); the glossary alone names the wrong form.
WRONG = 'orthopol' + 'itic'
TEXT = {'.md', '.py', '.json', '.txt', '.toml', '.cfg', ''}


class Terminology(unittest.TestCase):
    def test_wrong_adjective_absent(self):
        try:
            files = subprocess.run(['git', 'ls-files'], cwd=ROOT, capture_output=True,
                                   text=True, check=True).stdout.split()
        except (OSError, subprocess.CalledProcessError):
            files = [str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()]
        hits = [f for f in files
                if Path(f).suffix in TEXT and f != 'docs/glossary.md' and (ROOT / f).is_file()
                and WRONG in (ROOT / f).read_text(errors='ignore').lower()]
        self.assertEqual(hits, [], f'Use "orthopolic", not "{WRONG}" (docs/glossary.md)')


if __name__ == '__main__':
    unittest.main()
