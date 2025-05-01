import pytest
from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    (
        "SlimmeMeterPortalDataPrepare.py",
        [
            "-y",
            "Sample files/data_202?_871687120058657526.xlsx",
        ],
     ),
    (
        "SlimmeMeterPortalGasDataPrepare.py",
        [
            "-y",
            "Sample files/data_202?_871687140002948685.xlsx",
        ],
     ),
]


def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
