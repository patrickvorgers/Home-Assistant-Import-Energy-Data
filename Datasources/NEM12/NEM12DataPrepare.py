import datetime
import sys
from pathlib import Path

import pandas as pd

# 1) Add engine to path (simple way to add the engine to the path)
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# 2) Import engine (supress linter warnings)
import DataPrepareEngine as engine # noqa: E402
from DataPrepareEngine import DataFilter, OutputFileDefinition # noqa: E402

# 3) Override DataPrepare engine globals
# Name of the energy provider
engine.energyProviderName = "NEM12"

# Inputfile(s): filename extension
engine.inputFileNameExtension = ".csv"
# Inputfile(s): Name of the column containing the date of the reading.
#               Use this in case date and time is combined in one field.
#               Use the numerical column index in case the column name is not available.
engine.inputFileDateColumnName = "date"
# Inputfile(s): Name of the column containing the time of the reading.
#               Leave empty in case date and time is combined in one field.
engine.inputFileTimeColumnName = "_Time"
# Inputfile(s): Date/time format used in the datacolumn.
#               Combine the format of the date and time in case date and time are two seperate fields.
engine.inputFileDateTimeColumnFormat = "%Y%m%d %H:%M"
# Inputfile(s): Only use hourly data (True) or use the data as is (False)
#               In case of True, the data will be filtered to only include hourly data.
#               It takes into account in case the data needs to be recalculated (source data not increasing).
#               Home Assistant uses hourly data, higher resolution will work but will impact performance.
engine.inputFileDateTimeOnlyUseHourly = True
# Inputfile(s): Data separator being used in the input file (only csv files)
engine.inputFileDataSeparator = ","
# Inputfile(s): Decimal token being used in the input file (csv and excel files)
engine.inputFileDataDecimal = "."
# Inputfile(s): Whether the input file has a header row from which header names can be derived (only csv files)
engine.inputFileHasHeaderNameRow = False
# Inputfile(s): Number of header rows in the input file (csv and excel files)
engine.inputFileNumHeaderRows = 1
# Inputfile(s): Number of footer rows in the input file (csv and excel files)
engine.inputFileNumFooterRows = 0

# List of one or more output file definitions
engine.outputFiles = [
    OutputFileDefinition(
        "elec_feed_in_tariff_1_high_resolution.csv",
        "_Value",
        # Exclude negative values
        [DataFilter("_Value", r"^(?:[1-9]\d*|0)?(?:\.\d+)?$", True)],
        True,
    ),
    OutputFileDefinition(
        "elec_feed_out_tariff_1_high_resolution.csv",
        "_Value",
        # Exclude positive values
        [DataFilter("_Value", r"^(?:[1-9]\d*|0)?(?:\.\d+)?$", False)],
        True,
    ),
]


# Prepare the input data (before date/time manipulation)
def customPrepareDataPre(dataFrame: pd.DataFrame) -> pd.DataFrame:
    df_clean = dataFrame.copy()

    # Filter rows where the first column (record type) equals 300
    filtered_df = df_clean[df_clean.iloc[:, 0] == 300].reset_index(drop=True)

    # Remove the record type column
    filtered_df = filtered_df.drop(columns=filtered_df.columns[0])

    # The first column is the date. Starting from the second column, we detect the
    # interval columns. We iterate until we hit the first non-numeric column.
    num_interval_cols = 0
    for col in filtered_df.columns[1:]:
        try:
            # Attempt to convert the first row's value to float.
            float(filtered_df[col].iloc[0])
            num_interval_cols += 1
        except (ValueError, TypeError):
            # Stop counting when a non-numeric value is found (e.g. a trailing field)
            break

    # Keep only the date and the numeric interval columns. The date is the first column,
    # and the interval values are the next num_interval_cols columns.
    cols_to_keep = [filtered_df.columns[0]] + list(
        filtered_df.columns[1 : 1 + num_interval_cols]
    )
    filtered_df = filtered_df[cols_to_keep]

    # Calculate the interval in minutes assuming a full day (1440 minutes) is covered by the
    # interval columns.If there are 288 columns, for instance, the interval will be 5 minutes.
    if num_interval_cols > 0:
        interval_minutes = 1440 / num_interval_cols
    else:
        raise ValueError("No numeric interval columns detected.")

    # Generate timestamps starting at 00:00 and increasing by the computed interval.
    start_time = datetime.datetime.strptime("00:00", "%H:%M")
    timestamps = [
        (start_time + datetime.timedelta(minutes=interval_minutes * i)).strftime(
            "%H:%M"
        )
        for i in range(num_interval_cols)
    ]

    # Rename the columns: first column becomes 'date',
    #  and the interval columns are labeled with the generated timestamps.
    new_columns = ["date"] + timestamps
    filtered_df.columns = new_columns

    # Remove duplicate dates if present.
    filtered_df = filtered_df.drop_duplicates(subset="date")

    # Reshape the DataFrame from wide to long format so that
    # each row contains a date, a time, and the corresponding value.
    df_melted = pd.melt(
        filtered_df, id_vars=["date"], var_name="_Time", value_name="_Value"
    )

    # Convert the _Value column to numeric (non-convertible values will become NaN)
    df_melted["_Value"] = pd.to_numeric(df_melted["_Value"], errors="coerce")

    return df_melted


# 4) Invoke DataPrepare engine
if __name__ == '__main__':
    # Set the hook functions
    engine.customPrepareDataPre = customPrepareDataPre

    engine.main()
