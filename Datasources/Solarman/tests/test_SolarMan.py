import pytest
from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    ("SolarmanDataPrepare.py", ["-y", "Sample files/Solarman-Daily.Statistics-20250316.xlsx"]),
]

def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
