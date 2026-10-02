"""Save generated figures with clean whitespace in their SVG source."""
from pathlib import Path


def save_figure(figure, path, *, dpi):
    path = Path(path)
    figure.savefig(path, dpi=dpi)
    if path.suffix.lower() == ".svg":
        path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
