from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    (
        "EnelDistribuzioneDataPrepare.py",
        ["-y", "Sample files/ExportData_settembre.csv"],
    ),
]


def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
