import sys
from pathlib import Path

# 1) Add engine to path (simple way to add the engine to the path)
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# 2) Import engine (supress linter warnings)
import DataPrepareEngine as engine  # noqa: E402
from DataPrepareEngine import IntervalMode, OutputFileDefinition  # noqa: E402

# 3) Override DataPrepare engine globals
# Name of the energy provider
engine.energyProviderName = "SMA"

# Inputfile(s): filename extension
engine.inputFileNameExtension = ".csv"
# Inputfile(s): Name of the column containing the date of the reading.
#               Use this in case date and time is combined in one field.
#               Use the numerical column index in case the column name is not available.
engine.inputFileDateColumnName = "DD.MM.YYYY hh:mm:ss"
# Inputfile(s): Date/time format used in the datacolumn.
#               Combine the format of the date and time in case date and time are two seperate fields.
engine.inputFileDateTimeColumnFormat = "%d.%m.%Y %H:%M:%S"
# Inputfile(s): Date/time UTC indication.
#               Set to True in case the date/time is in UTC, False in case it is in local time.
engine.inputFileDateTimeIsUTC = False
# Inputfile(s): Only use hourly data (True) or use the data as is (False)
#               In case of True, the data will be filtered to only include hourly data.
#               It takes into account in case the data needs to be recalculated (source data not increasing).
#               Home Assistant uses hourly data, higher resolution will work but will impact performance.
engine.inputFileDateTimeOnlyUseHourly = True
# Inputfile(s): Invalid values in the input file will be removed otherwise they will be replaced with 0.
engine.inputFileDataRemoveInvalidValues = True
# Inputfile(s): Data separator being used in the input file (only csv files)
engine.inputFileDataSeparator = ","
# Inputfile(s): Decimal token being used in the input file (csv and excel files)
engine.inputFileDataDecimal = "."
# Inputfile(s): Whether the input file has a header row from which header names can be derived (only csv files)
engine.inputFileHasHeaderNameRow = True
# Inputfile(s): Number of header rows in the input file (csv and excel files)
engine.inputFileNumHeaderRows = 8
# Inputfile(s): Number of footer rows in the input file (csv and excel files)
engine.inputFileNumFooterRows = 0

# List of one or more output file definitions
engine.outputFiles = [
    # The columnname [Wh] needs to be escaped to prevent regex issues
    OutputFileDefinition(
        "elec_solar_high_resolution.csv",
        "[[]Wh[]]",
        [],
        IntervalMode.READING_END_INTERVAL,
    ),
    # The columnname [Wh] needs to be escaped to prevent regex issues
    OutputFileDefinition(
        "elec_solar_low_resolution.csv",
        "[[]Wh[]]",
        [],
        IntervalMode.READING_END_INTERVAL,
    ),
]


# 4) Invoke DataPrepare engine
if __name__ == "__main__":
    engine.main()
