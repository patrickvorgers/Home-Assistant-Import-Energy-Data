import pytest
from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    ("NextEnergyDataPrepare.py", ["-y", "Sample files/Measurements 19-01-2024 accesspointId 99999.xlsx"]),
]

def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
