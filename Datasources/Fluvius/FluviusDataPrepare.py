import sys
from pathlib import Path

# 1) Add engine to path (simple way to add the engine to the path)
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# 2) Import engine (supress linter warnings)
import DataPrepareEngine as engine  # noqa: E402
from DataPrepareEngine import DataFilter, OutputFileDefinition  # noqa: E402

# 3) Override DataPrepare engine globals
# Name of the energy provider
engine.energyProviderName = "Fluvius"

# Inputfile(s): filename extension
engine.inputFileNameExtension = ".csv"
# Inputfile(s): Name of the column containing the date of the reading.
#               Use this in case date and time is combined in one field.
#               Use the numerical column index in case the column name is not available.
engine.inputFileDateColumnName = "Tot datum"
# Inputfile(s): Name of the column containing the time of the reading.
#               Leave empty in case date and time is combined in one field.
engine.inputFileTimeColumnName = "Tot tijdstip"
# Inputfile(s): Date/time format used in the datacolumn.
#               Combine the format of the date and time in case date and time are two seperate fields.
engine.inputFileDateTimeColumnFormat = "%d-%m-%Y %H:%M:%S"
# Inputfile(s): Data separator being used in the input file (only csv files)
engine.inputFileDataSeparator = ";"
# Inputfile(s): Decimal token being used in the input file (csv and excel files)
engine.inputFileDataDecimal = ","
# Inputfile(s): Whether the input file has a header row from which header names can be derived (only csv files)
engine.inputFileHasHeaderNameRow = True
# Inputfile(s): Number of header rows in the input file (csv and excel files)
engine.inputFileNumHeaderRows = 0
# Inputfile(s): Number of footer rows in the input file (csv and excel files)
engine.inputFileNumFooterRows = 0

# List of one or more output file definitions
engine.outputFiles = [
    OutputFileDefinition(
        "elec_feed_in_tariff_1_high_resolution.csv",
        "Volume",
        [
            DataFilter("Register", "Afname Dag", True),
            DataFilter("Eenheid", "kWh", True),
        ],
        True,
    ),
    OutputFileDefinition(
        "elec_feed_in_tariff_2_high_resolution.csv",
        "Volume",
        [
            DataFilter("Register", "Afname Nacht", True),
            DataFilter("Eenheid", "kWh", True),
        ],
        True,
    ),
    OutputFileDefinition(
        "elec_feed_out_tariff_1_high_resolution.csv",
        "Volume",
        [
            DataFilter("Register", "Injectie Dag", True),
            DataFilter("Eenheid", "kWh", True),
        ],
        True,
    ),
    OutputFileDefinition(
        "elec_feed_out_tariff_2_high_resolution.csv",
        "Volume",
        [
            DataFilter("Register", "Injectie Nacht", True),
            DataFilter("Eenheid", "kWh", True),
        ],
        True,
    ),
    OutputFileDefinition(
        "gas_high_resolution.csv",
        "Volume",
        [
            DataFilter("Register", "Afname", True),
            DataFilter("Eenheid", "m³", True),
        ],
        True,
    ),
]


# 4) Invoke DataPrepare engine
if __name__ == "__main__":
    engine.main()
