import sys
from datetime import time
from pathlib import Path

import pandas as pd

# 1) Add engine to path (simple way to add the engine to the path)
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# 2) Import engine (supress linter warnings)
import DataPrepareEngine as engine  # noqa: E402
from DataPrepareEngine import (  # noqa: E402
    DataFilter,
    IntervalMode,
    OutputFileDefinition,
)

# 3) Override DataPrepare engine globals
# Name of the energy provider
engine.energyProviderName = "Energiemanager"

# Inputfile(s): filename extension
engine.inputFileNameExtension = ".csv"
# Inputfile(s): Name of the column containing the date of the reading.
#               Use this in case date and time is combined in one field.
#               Use the numerical column index in case the column name is not available.
engine.inputFileDateColumnName = "moment-date"
# Inputfile(s): Date/time format used in the datacolumn.
#               Combine the format of the date and time in case date and time are two seperate fields.
engine.inputFileDateTimeColumnFormat = "%Y-%m-%d %H:%M:%S"
# Inputfile(s): Date/time UTC indication
#               Set to True in case the date/time is in UTC, False in case it is in local time.
engine.inputFileDateTimeIsUTC = False
# Inputfile(s): Name of the timezone of the input data
#               The IANA timezone name of the input data (so that DST can be correctly applied).
#               Example: "Europe/Amsterdam", "America/New_York".
#               Leave as empty string to auto-detect from the local machine.
#               Setting is only needed when the setting inputFileDateTimeIsUTC is False.
engine.inputFileTimeZoneName = "Europe/Amsterdam"
# Inputfile(s): Only use hourly data (True) or use the data as is (False)
#               In case of True, the data will be filtered to only include hourly data.
#               It takes into account in case the data needs to be recalculated (source data not increasing).
#               Home Assistant uses hourly data, higher resolution will work but will impact performance.
engine.inputFileDateTimeOnlyUseHourly = True
# Inputfile(s): Invalid values in the input file will be removed otherwise they will be replaced with 0.
engine.inputFileDataRemoveInvalidValues = False
# Inputfile(s): Data separator being used in the input file (only csv files)
engine.inputFileDataSeparator = ";"
# Inputfile(s): Decimal token being used in the input file (csv and excel files)
engine.inputFileDataDecimal = "."
# Inputfile(s): Whether the input file has a header row from which header names can be derived (only csv files)
engine.inputFileHasHeaderNameRow = True
# Inputfile(s): Number of header rows in the input file (csv and excel files)
engine.inputFileNumHeaderRows = 1
# Inputfile(s): Number of footer rows in the input file (csv and excel files)
engine.inputFileNumFooterRows = 0

# Name used for the temporary date/time field.
# This needs normally no change only when it conflicts with existing columns.
engine.dateTimeColumnName = "_DateTime"

# List of one or more output file definitions
engine.outputFiles = [
    OutputFileDefinition(
        "elec_feed_in_tariff_1_high_resolution.csv",
        "usage",
        [
            DataFilter("code", "^ellm$", True),
            DataFilter("Tariff", "1", True),
        ],
        intervalMode=IntervalMode.USAGE,
    ),
    OutputFileDefinition(
        "elec_feed_in_tariff_2_high_resolution.csv",
        "usage",
        [
            DataFilter("code", "^ellm$", True),
            DataFilter("Tariff", "2", True),
        ],
        intervalMode=IntervalMode.USAGE,
    ),
    OutputFileDefinition(
        "elec_feed_out_tariff_1_high_resolution.csv",
        "usage",
        [
            DataFilter("code", "^eltm$", True),
            DataFilter("Tariff", "1", True),
        ],
        intervalMode=IntervalMode.USAGE,
    ),
    OutputFileDefinition(
        "elec_feed_out_tariff_2_high_resolution.csv",
        "usage",
        [
            DataFilter("code", "^eltm$", True),
            DataFilter("Tariff", "2", True),
        ],
        intervalMode=IntervalMode.USAGE,
    ),
    OutputFileDefinition(
        "gas_high_resolution.csv", "value", [DataFilter("code", "agasm$", True)]
    ),
]


# Determine the tariff based on the date and time of the record
def determine_tariff(recordDatetime: pd.Timestamp) -> int:
    """
    Tariff:
    - Tariff 1 = normal / high
    - Tariff 2 = low
    Assumptions:
    - Monday - Friday 07:00-23:00 => Tariff 1
    - Remaining hours + and weekend => Tariff 2

    Check your sensors to verify which tariffs apply. So it can be that for your sensors
    Tariff 1 is the low tariff and Tariff 2 is the high tariff, in that case you can just
    swap the sensor definition in the SQL script.
    """
    # weekday(): monday=0 ... sunday=6
    if recordDatetime.weekday() <= 4:
        if time(7, 0) <= recordDatetime.time() < time(23, 0):
            return 1
    return 2


# Prepare the input data (after date/time manipulation)
def customPrepareDataPost(dataFrame: pd.DataFrame) -> pd.DataFrame:
    df = dataFrame.copy()

    # Make sure value column is numeric, invalid values will be replaced with 0
    df["value"] = pd.to_numeric(df["value"], errors="coerce").fillna(0)

    # Convert unix timestamp to datetime (in UTC) and convert to local timezone
    dt = pd.to_datetime(
        df[engine.dateTimeColumnName], unit="s", utc=True
    ).dt.tz_convert(engine.inputFileTimeZoneName)

    # Determine the tariff based on the date and time of the record
    df["Tariff"] = dt.map(determine_tariff)

    # Sort on code and date to make sure the diff function works correctly
    df = df.sort_values(by=["code", engine.dateTimeColumnName]).reset_index(drop=True)

    # Determine delta per code based on cumulative meter readings
    df["usage"] = df.groupby("code")["value"].diff()

    # First value per code has no previous value to compare with
    df["usage"] = df["usage"].fillna(0)

    # Remove invalid negative deltas by setting them to 0, this can occur due to meter resets or faulty data
    df.loc[df["usage"] < 0, "usage"] = 0

    return df


# 4) Invoke DataPrepare engine
if __name__ == "__main__":
    # Set the hook function
    engine.customPrepareDataPost = customPrepareDataPost

    engine.main()
