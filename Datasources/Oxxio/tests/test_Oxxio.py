import pytest
from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    ("OxxioDataPrepare.py", ["-y", "Sample files/Oxxio.Verbruik_05-06-2023-22-01-2024.xlsx"]),
]

def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
