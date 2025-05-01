import pytest
from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    (
        "GreenChoiceDataPrepare.py", ["-y", "Sample files/meterstanden_stroom_2023.csv"],
    ),
]

def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
