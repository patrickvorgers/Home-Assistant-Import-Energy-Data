"""Integration tests for the E-REDES data preparation script."""

from tests.helpers import run_commands


COMMANDS = [
    ("ERedesDataPrepare.py", ["-y", "Sample files/e-redes-sample.xlsx"]),
]


def test_commands(repo_root):
    """Execute the script and verify generated CSV against the sample."""
    run_commands(repo_root, COMMANDS)

