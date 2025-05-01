from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    (
        "FluviusDataPrepare.py",
        [
            "-y",
            "Sample files/Verbruikshistoriek_elektriciteit_123456789123456789_20211012_20240929_kwartiertotalen.csv",
        ],
    ),
    (
        "FluviusDataPrepare.py",
        [
            "-y",
            "Sample files/Verbruikshistoriek_gas_123456789123456789_20220110_20240929_uurtotalen.csv",
            "gas_high_resolution.csv",
        ],
    ),
    (
        "FluviusDataPrepareEN.py",
        [
            "-y",
            "Sample files/Consumption_history_electricity_541448820052377134_20231022_20250426_15 minute totals.csv",
        ],
    ),
    (
        "FluviusDataPrepareEN.py",
        [
            "-y",
            "Sample files/Consumption_history_gas_541448860018322037_20231022_20250426_hourly totals.csv",
            "gas_consumed_high_resolution.csv",
        ],
    ),
]


def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
