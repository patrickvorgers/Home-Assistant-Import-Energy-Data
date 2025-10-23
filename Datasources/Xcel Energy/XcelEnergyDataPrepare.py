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
engine.energyProviderName = "Xcel Energy"

# Inputfile(s): filename extension
engine.inputFileNameExtension = ".csv"
# Inputfile(s): Name of the column containing the date of the reading.
engine.inputFileDateColumnName = "Bill Date"
# Inputfile(s): Name of the column containing the time of the reading.
engine.inputFileTimeColumnName = ""
# Inputfile(s): Date/time format used in the datacolumn.
engine.inputFileDateTimeColumnFormat = "%m/%d/%Y"
# Inputfile(s): Date/time UTC indication
engine.inputFileDateTimeIsUTC = False
# Inputfile(s): Name of the timezone of the input data
engine.inputFileTimeZoneName = ""
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

# List of output file definitions - will be populated dynamically based on input data
# Xcel Energy Bill History CSV can provide:
# - Gas Usage (Therms) and Gas Charges ($) - gas only accounts
# - Electric Usage (kWh) and Electric Charges ($) - electric only accounts
# - Both gas and electric data - dual service accounts
engine.outputFiles = []


def customReadInputFile(inputFileName: str) -> pd.DataFrame:
    """
    Custom file reader that detects available columns and sets up output files dynamically.
    """
    print(f"Loading data: {inputFileName}")

    # Read the CSV file
    dataFrame = pd.read_csv(
        inputFileName,
        sep=engine.inputFileDataSeparator,
        decimal=engine.inputFileDataDecimal,
        skiprows=engine.inputFileNumHeaderRows,
        skipfooter=engine.inputFileNumFooterRows,
        engine="python" if engine.inputFileNumFooterRows > 0 else "c",
    )

    # Remove any empty rows
    dataFrame = dataFrame.dropna(how="all")

    # Check what columns we have
    print(f"Columns found: {list(dataFrame.columns)}")

    # Check if we have gas or electric data
    has_gas = "Gas Usage (Therms)" in dataFrame.columns
    has_electric = "Electric Usage (kWh)" in dataFrame.columns

    # Dynamically create output file definitions based on available data
    output_files = []

    if has_gas:
        gas_mask = dataFrame["Gas Usage (Therms)"].notna()
        gas_mask &= dataFrame["Gas Usage (Therms)"] != 0
        gas_rows = len(dataFrame[gas_mask])
        print(f"Found Gas Usage data with {gas_rows} non-zero rows")
        output_files.append(
            OutputFileDefinition(
                "gas_high_resolution.csv",
                "Gas Usage (Therms)",
                [],
                IntervalMode.USAGE,
            )
        )

    if has_electric:
        electric_mask = dataFrame["Electric Usage (kWh)"].notna()
        electric_mask &= dataFrame["Electric Usage (kWh)"] != 0
        electric_rows = len(dataFrame[electric_mask])
        print(f"Found Electric Usage data with {electric_rows} non-zero rows")
        output_files.append(
            OutputFileDefinition(
                "elec_feed_in_tariff_1_high_resolution.csv",
                "Electric Usage (kWh)",
                [],
                IntervalMode.USAGE,
            )
        )

    if not output_files:
        raise ValueError("No gas or electric usage data found in the CSV file!")

    # Set the output files dynamically
    engine.outputFiles = output_files

    return dataFrame


def customPrepareDataPre(dataFrame: pd.DataFrame) -> pd.DataFrame:
    """
    Xcel Energy Bill History CSV format has:
    - "Bill Date" column with dates in MM/DD/YYYY format
    - "Gas Usage (Therms)" column for gas consumption (if gas account)
    - "Gas Charges" column for gas costs (if gas account)
    - "Electric Usage (kWh)" column for electricity consumption (if electric account)
    - "Electric Charges" column for electricity costs (if electric account)

    Data is ordered from newest to oldest (most recent bill first).
    """
    print("Preprocessing Xcel Energy Bill History data...")

    # Data is already cleaned by customReadInputFile
    return dataFrame


# Set the custom functions
engine.readInputFile = customReadInputFile
engine.customPrepareDataPre = customPrepareDataPre


# 4) Invoke DataPrepare engine
if __name__ == "__main__":
    engine.main()
