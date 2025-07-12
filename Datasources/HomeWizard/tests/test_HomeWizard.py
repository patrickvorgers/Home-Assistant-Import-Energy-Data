from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    (
        "HomeWizardDataPrepare.py",
        [
            "-y",
            "Sample files/homewizard_2022-09_15min_elec.csv",
        ],
    ),
    (
        "HomeWizardGasDataPrepare.py",
        [
            "-y",
            "Sample files/15min_P1g-2025-3-1-2025-7-12.csv",
        ],
    ),
    (
        "HomeWizardWaterDataPrepare.py",
        [
            "-y",
            "Sample files/15min_Water-2025-3-1-2025-7-12.csv",
        ],
    ),
    (
        "HomeWizardMeterDataPrepare.py",
        [
            "-y",
            "Sample files/15min_3_phase_kwh_meter-2025-3-1-2025-7-12.csv",
        ],
    ),
]


def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
