import pytest
from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    ("EnphaseDataPrepare.py", ["-y", "Sample files/9999998_custom_report.csv"]),
]


def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)

