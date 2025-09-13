"""Integration tests for the E-REDES data preparation script."""

from pathlib import Path

import pandas as pd

from tests.helpers import run_commands


COMMANDS = [
    ("ERedesDataPrepare.py", ["-y", "Sample files/e-redes-sample.xlsx"]),
]


def test_commands(repo_root):
    """Execute the script and verify generated CSV against the sample."""
    run_commands(repo_root, COMMANDS)


def test_header_at_row_one(repo_root):
    """Header row may appear at the very top if preamble rows are removed."""

    source_dir = Path(__file__).resolve().parent.parent
    sample_dir = source_dir / "Sample files"
    original = sample_dir / "e-redes-sample.xlsx"
    modified = sample_dir / "e-redes-sample-row1.xlsx"

    # Create a new export where the header is the first row
    df = pd.read_excel(original, header=7)
    df.to_excel(modified, index=False)

    try:
        run_commands(
            repo_root,
            [("ERedesDataPrepare.py", ["-y", f"Sample files/{modified.name}"])],
        )
    finally:
        if modified.exists():
            modified.unlink()

