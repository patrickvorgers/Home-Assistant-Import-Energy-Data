import pytest
from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    ("EnecoDataPrepare.py", ["-y", "Sample files/Verbruik_01-01-2020-31-12-2020.xlsx"]),
]

def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)

