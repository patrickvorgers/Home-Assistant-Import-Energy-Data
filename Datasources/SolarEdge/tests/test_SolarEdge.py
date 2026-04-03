from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS_NO_UTC = [
    ("SolarEdgeDataPrepare.py", ["-y", "Sample files/No UTC/solaredge.json"]),
]

COMMANDS_UTC = [
    ("SolarEdgeDataPrepare.py", ["-y", "Sample files/UTC/solaredge_????_??.json"]),
]


def test_commands_no_utc(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS_NO_UTC, r"Sample files/No UTC")


def test_commands_utc(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS_UTC, r"Sample files/UTC")
