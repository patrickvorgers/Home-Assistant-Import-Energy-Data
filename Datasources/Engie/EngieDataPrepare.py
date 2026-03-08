import sys
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
engine.energyProviderName = "Engie"

# Inputfile(s): filename extension
engine.inputFileNameExtension = ".csv"
# Inputfile(s): Name of the column containing the date of the reading.
#               Use this in case date and time is combined in one field.
#               Use the numerical column index in case the column name is not available.
engine.inputFileDateColumnName = "Datum"
# Inputfile(s): Date/time format used in the datacolumn.
#               Combine the format of the date and time in case date and time are two seperate fields.
engine.inputFileDateTimeColumnFormat = "%Y-%m-%dT%H:%M:%S%z"
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
        "Verbruik",
        [DataFilter("Type", "Elektriciteit", True), DataFilter("Piek", "true", True)],
        IntervalMode.USAGE,
    ),
    OutputFileDefinition(
        "elec_feed_in_tariff_2_high_resolution.csv",
        "Verbruik",
        [DataFilter("Type", "Elektriciteit", True), DataFilter("Piek", "false", True)],
        IntervalMode.USAGE,
    ),
    OutputFileDefinition(
        "elec_feed_out_tariff_1_high_resolution.csv",
        "Verbruik",
        [DataFilter("Type", "Teruglevering", True), DataFilter("Piek", "true", True)],
        IntervalMode.USAGE,
    ),
    OutputFileDefinition(
        "elec_feed_out_tariff_2_high_resolution.csv",
        "Verbruik",
        [DataFilter("Type", "Teruglevering", True), DataFilter("Piek", "false", True)],
        IntervalMode.USAGE,
    ),
    OutputFileDefinition(
        "gas_high_resolution.csv",
        "Verbruik",
        [DataFilter("Type", "Gas", True)],
        IntervalMode.USAGE,
    ),
]


# Prepare the input data (after date/time manipulation)
def customPrepareDataPost(dataFrame: pd.DataFrame) -> pd.DataFrame:
    if "Piek" in dataFrame.columns:
        # Force string + normalize to lowercase so True/False and "true"/"false" behave the same
        # Gas entries will have 0 in the Piek column which automatically forces the column to be string.
        # In case there are no Gas entries, we still need to force the column to string.
        dataFrame["Piek"] = dataFrame["Piek"].astype("string").str.strip().str.lower()

    return dataFrame


# 4) Invoke DataPrepare engine
if __name__ == "__main__":
    # Set the hook functions
    engine.customPrepareDataPost = customPrepareDataPost

    engine.main()
