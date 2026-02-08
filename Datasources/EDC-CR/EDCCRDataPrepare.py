import sys
from pathlib import Path

import pandas as pd

# 1) Add engine to path (simple way to add the engine to the path)
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# 2) Import engine (suppress linter warnings)
import DataPrepareEngine as engine  # noqa: E402
from DataPrepareEngine import IntervalMode, OutputFileDefinition  # noqa: E402

# 3) Override DataPrepare engine globals
# Name of the energy provider
engine.energyProviderName = "EDC-CR"

# Inputfile(s): filename extension
engine.inputFileNameExtension = ".csv"

# Inputfile(s): Name of the column containing the date of the reading.
#               Use this in case date and time is combined in one field.
#               Use the numerical column index in case the column name is not available.
engine.inputFileDateColumnName = "Datum"

# Inputfile(s): Name of the column containing the time of the reading.
#               Leave empty in case date and time is combined in one field.
#               Using "Cas od" (start time) for the timestamp
engine.inputFileTimeColumnName = "Cas od"

# Inputfile(s): Date/time format used in the datacolumn.
#               Combine the format of the date and time in case date and time are two separate fields.
engine.inputFileDateTimeColumnFormat = "%d.%m.%Y %H:%M"

# Inputfile(s): Date/time UTC indication
#               Set to True in case the date/time is in UTC, False in case it is in local time.
#               Czech data is in local time (Europe/Prague)
engine.inputFileDateTimeIsUTC = False

# Inputfile(s): Name of the timezone of the input data
#               The IANA timezone name of the input data (so that DST can be correctly applied).
engine.inputFileTimeZoneName = "Europe/Prague"

# Inputfile(s): Only use hourly data (True) or use the data as is (False)
#               Aggregates 15-minute data to hourly for better Home Assistant performance.
engine.inputFileDateTimeOnlyUseHourly = True

# Inputfile(s): Invalid values in the input file will be removed otherwise they will be replaced with 0.
engine.inputFileDataRemoveInvalidValues = False

# Inputfile(s): Remove zero values in the input file. Some datasources have zero values where no data is available.
engine.inputFileDataRemoveZeroValues = False

# Inputfile(s): Data separator being used in the input file (only csv files)
#               Czech CSV files use semicolon as separator
engine.inputFileDataSeparator = ";"

# Inputfile(s): Decimal token being used in the input file (csv and excel files)
#               Czech format uses comma as decimal separator (e.g., 0,25 = 0.25)
engine.inputFileDataDecimal = ","

# Inputfile(s): Whether the input file has a header row from which header names can be derived (only csv files)
engine.inputFileHasHeaderNameRow = True

# Inputfile(s): Number of header rows in the input file (csv and excel files)
engine.inputFileNumHeaderRows = 0

# Inputfile(s): Number of footer rows in the input file (csv and excel files)
engine.inputFileNumFooterRows = 0

# List of one or more output file definitions
# Using wildcard pattern to match the Producer-Consumer EAN column header (format: "NNNN-NNNN")
# IntervalMode.USAGE because the data is consumption per 15-minute interval, not cumulative readings
engine.outputFiles = [
    OutputFileDefinition(
        "elec_solar_high_resolution.csv",
        "*-*",  # Wildcard pattern to match the EAN column (e.g., "123456789-987654321")
        [],  # No filters needed - single meter data
        IntervalMode.USAGE,  # Data is usage per interval, not cumulative meter readings
        # Optional: Add initialValue if you have a known starting reading to avoid data spikes
        # initialValue=0,
    ),
]


# Prepare the input data (before date/time manipulation)
def customPrepareDataPre(dataFrame: pd.DataFrame) -> pd.DataFrame:
    return dataFrame


# Prepare the input data (after date/time manipulation)
def customPrepareDataPost(dataFrame: pd.DataFrame) -> pd.DataFrame:
    # Default no manipulation, add code if needed
    return dataFrame


# 4) Invoke DataPrepare engine
if __name__ == "__main__":
    # Set the hook functions
    engine.customPrepareDataPre = customPrepareDataPre
    engine.customPrepareDataPost = customPrepareDataPost

    engine.main()
