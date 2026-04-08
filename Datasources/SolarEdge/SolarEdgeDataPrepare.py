import re
import sys
from pathlib import Path

import pandas as pd

# 1) Add engine to path (simple way to add the engine to the path)
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# 2) Import engine (supress linter warnings)
import DataPrepareEngine as engine  # noqa: E402
from DataPrepareEngine import IntervalMode, OutputFileDefinition  # noqa: E402

# 3) Override DataPrepare engine globals
# Name of the energy provider
engine.energyProviderName = "SolarEdge"

# Inputfile(s): filename extension
engine.inputFileNameExtension = ".json"
# Inputfile(s): Name of the column containing the date of the reading.
#               Use this in case date and time is combined in one field.
#               Use the numerical column index in case the column name is not available.
engine.inputFileDateColumnName = "date"
# Inputfile(s): Date/time format used in the datacolumn.
#               Combine the format of the date and time in case date and time are two seperate fields.
engine.inputFileDateTimeColumnFormat = "%Y-%m-%d %H:%M:%S %z"
# Inputfile(s): Date/time UTC indication
#               Set to True in case the date/time is in UTC, False in case it is in local time.
engine.inputFileDateTimeIsUTC = True
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
# Inputfile(s): Name of the timezone of the input data
#               The IANA timezone name of the input data (so that DST can be correctly applied).
#               Example: "Europe/Amsterdam", "America/New_York".
#               Leave as empty string to auto-detect from the local machine.
#               Setting is only needed when the setting inputFileDateTimeIsUTC is False.
engine.inputFileTimeZoneName = "Europe/Amsterdam"
# Inputfile(s): Json path of the records (only needed for json files)
# Example: inputFileJsonPath: List[str] = ['energy', 'values']
engine.inputFileJsonPath = ["energy", "values"]

# List of one or more output file definitions
engine.outputFiles = [
    OutputFileDefinition(
        "elec_solar_high_resolution.csv",
        "value",
        [],
        IntervalMode.USAGE,
    ),
]


# Prepare the input data (before date/time manipulation)
def customPrepareDataPre(dataFrame: pd.DataFrame) -> pd.DataFrame:
    df = dataFrame.copy()

    sampleSeries = df["date"].dropna().astype(str).str.strip()
    if sampleSeries.empty:
        raise ValueError("No valid date values found in input data.")

    sample = sampleSeries.iloc[0]

    # Detect numeric timezone offset at end, e.g. +0200 or -0500
    if re.search(r"[+-]\d{4}$", sample):
        # Remove the middle timezone token and keep the trailing numeric offset
        # 2018-04-02 13:00:00 CEST+0200 -> 2018-04-02 13:00:00 +0200
        # 2018-12-01 13:00:00 CET+0100 -> 2018-12-01 13:00:00 +0100
        df["date"] = (
            df["date"]
            .astype(str)
            .str.replace(
                r"\s+\S+([+-]\d{4})$",
                r" \1",
                regex=True,
            )
        )

        engine.inputFileDateTimeColumnFormat = "%Y-%m-%d %H:%M:%S %z"
        engine.inputFileDateTimeIsUTC = True
    else:
        engine.inputFileDateTimeColumnFormat = "%Y-%m-%d %H:%M:%S"
        engine.inputFileDateTimeIsUTC = False

    return df


# 4) Invoke DataPrepare engine
if __name__ == "__main__":
    engine.customPrepareDataPre = customPrepareDataPre
    engine.main()
