from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    ("HomeWizardDataPrepare.py", ["-y", "Sample files/homewizard_2022-09_15min_elec.csv",]),
]


def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
