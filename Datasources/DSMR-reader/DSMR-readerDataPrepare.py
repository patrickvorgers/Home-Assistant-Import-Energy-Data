import sys
from pathlib import Path

import pandas as pd

# 1) Add engine to path (simple way to add the engine to the path)
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# 2) Import engine (supress linter warnings)
import DataPrepareEngine as engine  # noqa: E402
from DataPrepareEngine import DataFilter, OutputFileDefinition  # noqa: E402

# 3) Override DataPrepare engine globals
# Name of the energy provider
engine.energyProviderName = "DSMR-reader"

# Inputfile(s): filename extension
engine.inputFileNameExtension = ".csv"
# Inputfile(s): Name of the column containing the date of the reading.
#               Use this in case date and time is combined in one field.
#               Use the numerical column index in case the column name is not available.
engine.inputFileDateColumnName = "Hour Start"
# Inputfile(s): Name of the column containing the time of the reading.
#               Leave empty in case date and time is combined in one field.
engine.inputFileTimeColumnName = ""
# Inputfile(s): Date/time format used in the datacolumn.
#               Combine the format of the date and time in case date and time are two seperate fields.
engine.inputFileDateTimeColumnFormat = "%Y-%m-%dT%H:%M:%S%z"

# Inputfile(s): Date/time UTC indication
#               Set to True in case the date/time is in UTC, False in case it is in local time.
engine.inputFileDateTimeIsUTC = True
# Inputfile(s): Name of the timezone of the input data
#               The IANA timezone name of the input data (so that DST can be correctly applied).
#               Example: "Europe/Amsterdam", "America/New_York".
#               Leave as empty string to auto-detect from the local machine.
#               Setting is only needed when the setting inputFileDateTimeIsUTC is False.
engine.inputFileTimeZoneName = ""
# Inputfile(s): Only use hourly data (True) or use the data as is (False)
#               In case of True, the data will be filtered to only include hourly data.
#               It takes into account in case the data needs to be recalculated (source data not increasing).
#               Home Assistant uses hourly data, higher resolution will work but will impact performance.
engine.inputFileDateTimeOnlyUseHourly = True
# Inputfile(s): Invalid values in the input file will be removed otherwise they will be replaced with 0.
engine.inputFileDataRemoveInvalidValues = False
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
# Inputfile(s): Json path of the records (only needed for json files)
# Example: inputFileJsonPath: List[str] = ['energy', 'values']
engine.inputFileJsonPath = []
# Inputfile(s): Name or index of the excel sheet (only needed for excel files containing more sheets,
#               leave at 0 for the first sheet)
engine.inputFileExcelSheetName = 0
# When processing SQLite .db files, specify the table name to load
engine.inputFileDbTableName = "data"

# Name used for the temporary date/time field.
# This needs normally no change only when it conflicts with existing columns.
engine.dateTimeColumnName = "_DateTime"

# List of one or more output file definitions
engine.outputFiles = [
    OutputFileDefinition(
        "elec_feed_in_tariff_1_high_resolution.csv",
        "Electricity 1 (Dutch Users: Low Tariff)",
        [],
    ),
    OutputFileDefinition(
        "elec_feed_in_tariff_2_high_resolution.csv",
        "Electricity 2 (Dutch Users: Normal Tariff)",
        [],
    ),
    OutputFileDefinition(
        "elec_feed_out_tariff_1_high_resolution.csv",
        "Electricity 1 Returned (Dutch Users: Low Tariff)",
        [],
    ),
    OutputFileDefinition(
        "elec_feed_out_tariff_2_high_resolution.csv",
        "Electricity 2 Returned (Dutch Users: Normal Tariff)",
        [],
    ),
    OutputFileDefinition("gas_high_resolution.csv", "Gas", []),
]


# Prepare the input data (after date/time manipulation)
def customPrepareDataPre(dataFrame: pd.DataFrame) -> pd.DataFrame:
    return dataFrame


# Prepare the input data (after date/time manipulation)
def customPrepareDataPost(dataFrame: pd.DataFrame) -> pd.DataFrame:
    # Default no manipulation, add code if needed

    # Example:
    #   dataFrame["Energy Produced (Wh)"] =
    #       dataFrame["Energy Produced (Wh)"].str.replace(',', '').replace('\"', '').astype(int)
    return dataFrame


# 4) Invoke DataPrepare engine
if __name__ == "__main__":
    # Set the hook functions
    engine.customPrepareDataPre = customPrepareDataPre
    engine.customPrepareDataPost = customPrepareDataPost

    engine.main()
