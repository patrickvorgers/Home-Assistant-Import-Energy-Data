from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    (
        "P1MonDataPrepare.py",
        [
            "-y",
            "Sample files/e_historie.db.xlsx",
        ],
    ),
    (
        "P1MonWaterDataPrepare.py",
        [
            "-y",
            "Sample files/06_watermeter.db.xlsx",
        ],
    ),
]


def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
