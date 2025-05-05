import sys
from pathlib import Path
from typing import List

import pandas as pd

# 1) Add engine to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# 2) Import engine
import DataPrepareEngine as engine
from DataPrepareEngine import DataFilter, OutputFileDefinition

# 3) Override DataPrepare engine globals
# Name of the energy provider
engine.energyProviderName = "Enel Distribuzione"

# Inputfile(s): filename extension
engine.inputFileNameExtension = ".csv"
# Inputfile(s): Name of the column containing the date of the reading.
#               Use this in case date and time is combined in one field.
#               Use the numerical column index in case the column name is not available.
engine.inputFileDateColumnName = "Giorno"
# Inputfile(s): Name of the column containing the time of the reading.
#               Leave empty in case date and time is combined in one field.
engine.inputFileTimeColumnName = "_Time"
# Inputfile(s): Date/time format used in the datacolumn.
#               Combine the format of the date and time in case date and time are two seperate fields.
engine.inputFileDateTimeColumnFormat = "%d/%m/%Y %H:%M"
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
        "_Value",
        [],
        True,
    ),
]


# Prepare the input data (before date/time manipulation)
def customPrepareDataPre(dataFrame: pd.DataFrame) -> pd.DataFrame:
    df_clean = dataFrame.copy()

    # Extract the 'from' part of each column header (before the hyphen)
    # If the column doesn't contain a hyphen, leave it as is
    df_clean.columns = [
        time.split("-")[0] if "-" in time else time for time in df_clean.columns
    ]

    # Melt the DataFrame to create 'Date', 'Time', and 'Value' columns
    df_melted = pd.melt(
        df_clean, id_vars=["Giorno"], var_name="_Time", value_name="_Value"
    )

    return df_melted


# 4) Invoke DataPrepare engine
if __name__ == '__main__':
    # Set the hook functions
    engine.customPrepareDataPre = customPrepareDataPre

    engine.main()
