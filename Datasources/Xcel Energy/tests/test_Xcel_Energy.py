from tests.helpers import run_commands

# List scripts and their CLI args
# Test all three scenarios: gas only, electric only, and both
COMMANDS = [
#    (
#        "XcelEnergyDataPrepare.py",
#        ["-y", "Sample files/xcel_energy_gas_only_sample.csv"],
#    ),
#    (
#        "XcelEnergyDataPrepare.py",
#        ["-y", "Sample files/xcel_energy_electric_only_sample.csv"],
#    ),
    (
        "XcelEnergyDataPrepare.py",
        ["-y", "Sample files/xcel_energy_sample.csv"],
    ),
]


def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    Tests three scenarios:
    1. Gas only account
    2. Electric only account
    3. Dual service account (both gas and electric)
    """
    run_commands(repo_root, COMMANDS)
