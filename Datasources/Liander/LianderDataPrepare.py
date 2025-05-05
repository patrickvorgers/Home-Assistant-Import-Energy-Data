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
engine.energyProviderName = "Liander"

# Inputfile(s): filename extension
engine.inputFileNameExtension = ".csv"
# Inputfile(s): Name of the column containing the date of the reading.
#               Use this in case date and time is combined in one field.
#               Use the numerical column index in case the column name is not available.
engine.inputFileDateColumnName = "meterreadingdate"
# Inputfile(s): Date/time format used in the datacolumn.
#               Combine the format of the date and time in case date and time are two seperate fields.
engine.inputFileDateTimeColumnFormat = "%d-%m-%Y"
# Inputfile(s): Data separator being used in the input file (only csv files)
engine.inputFileDataSeparator = ","
# Inputfile(s): Decimal token being used in the input file (csv and excel files)
engine.inputFileDataDecimal = "."
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
        "reading2",
        [DataFilter("meternummer", "^E", True)],
        False,
    ),
    OutputFileDefinition(
        "elec_feed_in_tariff_2_high_resolution.csv",
        "reading1",
        [DataFilter("meternummer", "^E", True)],
        False,
    ),
    OutputFileDefinition(
        "elec_feed_out_tariff_1_high_resolution.csv",
        "reading4",
        [DataFilter("meternummer", "^E", True)],
        False,
    ),
    OutputFileDefinition(
        "elec_feed_out_tariff_2_high_resolution.csv",
        "reading3",
        [DataFilter("meternummer", "^E", True)],
        False,
    ),
    OutputFileDefinition(
        "gas_high_resolution.csv",
        "reading1",
        [DataFilter("meternummer", "^G", True)],
        False,
    ),
]


# 4) Invoke DataPrepare engine
if __name__ == '__main__':
    engine.main()
