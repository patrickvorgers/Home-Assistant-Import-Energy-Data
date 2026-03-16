from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    (
        "InfluxDbChronografDataPrepare.py",
        [
            "-y",
            "Sample files/2026-03-14-21-49 Chronograf Data.csv",
        ],
    ),
]


def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
