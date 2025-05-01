import pytest
from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    ("ZonneplanDataPrepare.py", ["-y", "Sample files/export-2025-01-21.11_17_12.xlsx"]),
]

def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
