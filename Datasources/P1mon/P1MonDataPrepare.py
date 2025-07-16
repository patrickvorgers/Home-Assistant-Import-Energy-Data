import sys
from pathlib import Path

# 1) Add engine to path (simple way to add the engine to the path)
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# 2) Import engine (supress linter warnings)
import DataPrepareEngine as engine  # noqa: E402
from DataPrepareEngine import OutputFileDefinition  # noqa: E402

# 3) Override DataPrepare engine globals
# Name of the energy provider
engine.energyProviderName = "P1Mon"

# Inputfile(s): filename extension
engine.inputFileNameExtension = ".xlsx"
# Inputfile(s): Name of the column containing the date of the reading.
#               Use this in case date and time is combined in one field.
#               Use the numerical column index in case the column name is not available.
engine.inputFileDateColumnName = "TIMESTAMP"
# Inputfile(s): Date/time format used in the datacolumn.
#               Combine the format of the date and time in case date and time are two seperate fields.
engine.inputFileDateTimeColumnFormat = "%Y-%m-%d %H:%M:%S"
# Inputfile(s): Date/time UTC indication.
#               Set to True in case the date/time is in UTC, False in case it is in local time.
engine.inputFileDateTimeIsUTC = False
# Inputfile(s): Decimal token being used in the input file (csv and excel files)
engine.inputFileDataDecimal = "."
# Inputfile(s): Number of header rows in the input file (csv and excel files)
engine.inputFileNumHeaderRows = 0
# Inputfile(s): Number of footer rows in the input file (csv and excel files)
engine.inputFileNumFooterRows = 0
# Inputfile(s): Name or index of the excel sheet (only needed for excel files containing more sheets,
#               leave at 0 for the first sheet)
engine.inputFileExcelSheetName = "e_history_uur"

# List of one or more output file definitions
engine.outputFiles = [
    OutputFileDefinition(
        "elec_feed_in_tariff_1_high_resolution.csv",
        "VERBR_KWH_182",
        [],
        False,
    ),  # High tariff
    OutputFileDefinition(
        "elec_feed_in_tariff_2_high_resolution.csv",
        "VERBR_KWH_181",
        [],
        False,
    ),  # Low tariff
    OutputFileDefinition(
        "elec_feed_out_tariff_1_high_resolution.csv",
        "GELVR_KWH_282",
        [],
        False,
    ),  # High tariff
    OutputFileDefinition(
        "elec_feed_out_tariff_2_high_resolution.csv",
        "GELVR_KWH_281",
        [],
        False,
    ),  # Low tariff
    OutputFileDefinition(
        "gas_high_resolution.csv",
        "VERBR_GAS_2421",
        [],
        False,
    ),
]


# 4) Invoke DataPrepare engine
if __name__ == "__main__":
    engine.main()
