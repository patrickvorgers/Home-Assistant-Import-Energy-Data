from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    (
        "ShellyEM3DataPrepare.py",
        [
            "-y",
            "-p phaseA",
            "Sample files/em_data_phaseA.csv",
        ],
    ),
    (
        "ShellyEM3DataPrepare.py",
        [
            "-y",
            "-p phaseB",
            "Sample files/em_data_phaseB.csv",
        ],
    ),
    (
        "ShellyEM3DataPrepare.py",
        [
            "-y",
            "-p phaseC",
            "Sample files/em_data_phaseC.csv",
        ],
    ),
]


def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
