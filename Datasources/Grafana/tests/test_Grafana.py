from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    (
        "GrafanaDataPrepare.py",
        [
            "-y",
            "Sample files/PV 11 meter-data-2026-03-15 12_41_54.csv",
        ],
    ),
]


def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
