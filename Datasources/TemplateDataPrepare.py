import argparse
import datetime
import glob
import json
import os
import sqlite3
import sys
import warnings
from typing import List, NamedTuple

import pandas as pd


# DataFilter named tuple definition
#   column: The name of the column on which the filter should be applied
#   value:  The value on which should be filtered (regular expressions can be used)
#   equal:  Boolean value indicating whether the filter should be inclusive or exclusive (True/False)
class DataFilter(NamedTuple):
    column: str
    value: str
    equal: bool


# OutputFileDefinition named tuple definition
#   outputFileName:  The name of the output file
#   valueColumnName: The name of the column holding the value.
#                    Use the column index in case the column name is not available.
#   dataFilters:     A list of datafilters (see above the definition of a datafilter)
#   recalculate:     Boolean value indication whether the data should be recalculated,
#                    because the source is not an increasing value
#   initialValue:    Starting reading to apply when recalculate=True. Use when the source`s first reading is known;
#                    otherwise, imported values are treated as relative increments without actual totals.
#                    Supplying an initialValue establishes a baseline and helps avoid a potentially large spike at
#                    the crossover between imported data and existing Home Assistant statistics - especially
#                    if the starting reading is below the cutoff_invalid_value.
class OutputFileDefinition(NamedTuple):
    outputFileName: str
    valueColumnName: str | int
    dataFilters: List[DataFilter]
    recalculate: bool
    initialValue: float = 0


# ---------------------------------------------------------------------------------------------------------------------
# TEMPLATE SETUP
# ---------------------------------------------------------------------------------------------------------------------

# Name of the energy provider
energyProviderName = "Template"

# Inputfile(s): filename extension
inputFileNameExtension = ".csv"
# Inputfile(s): Name of the column containing the date of the reading.
#               Use this in case date and time is combined in one field.
#               Use the numerical column index in case the column name is not available.
inputFileDateColumnName = "meterreadingdate"
# Inputfile(s): Name of the column containing the time of the reading.
#               Leave empty in case date and time is combined in one field.
inputFileTimeColumnName = ""
# Inputfile(s): Date/time format used in the datacolumn.
#               Combine the format of the date and time in case date and time are two seperate fields.
inputFileDateTimeColumnFormat = "%d-%m-%Y"
# Inputfile(s): Only use hourly data (True) or use the data as is (False)
#               In case of True, the data will be filtered to only include hourly data.
#               It takes into account in case the data needs to be recalculated (source data not increasing).
#               Home Assistant uses hourly data, higher resolution will work but will impact performance.
inputFileDateTimeOnlyUseHourly = False
# Inputfile(s): Data separator being used in the .csv input file
inputFileDataSeparator = ","
# Inputfile(s): Decimal token being used in the input file
inputFileDataDecimal = "."
# Inputfile(s): Whether the input file has a header row from which header names can be derived
inputFileHasHeaderNameRow = True
# Inputfile(s): Number of header rows in the input file
inputFileNumHeaderRows = 0
# Inputfile(s): Number of footer rows in the input file
inputFileNumFooterRows = 0
# Inputfile(s): Json path of the records (only needed for json files)
# Example: inputFileJsonPath: List[str] = ['energy', 'values']
inputFileJsonPath: List[str] = []
# Inputfile(s): Name or index of the excel sheet (only needed for excel files containing more sheets,
#               leave at 0 for the first sheet)
inputFileExcelSheetName = 0
# When processing SQLite .db files, specify the table name to load
inputFileDbTableName = "data"

# Name used for the temporary date/time field.
# This needs normally no change only when it conflicts with existing columns.
dateTimeColumnName = "_DateTime"

# List of one or more output file definitions
outputFiles = [
    OutputFileDefinition(
        "elec_feed_in_tariff_1_high_resolution.csv",
        "reading2",
        [DataFilter("meternummer", "^E", True)],
        False,
    ),
    OutputFileDefinition(
        "elec_feed_in_tariff_2_high_resolution.csv",
        "reading1",
        [DataFilter("meternummer", "^E", True)],
        False,
    ),
    OutputFileDefinition(
        "elec_feed_out_tariff_1_high_resolution.csv",
        "reading4",
        [DataFilter("meternummer", "^E", True)],
        False,
    ),
    OutputFileDefinition(
        "elec_feed_out_tariff_2_high_resolution.csv",
        "reading3",
        [DataFilter("meternummer", "^E", True)],
        False,
    ),
    OutputFileDefinition(
        "gas_high_resolution.csv",
        "reading1",
        [DataFilter("meternummer", "^G", True)],
        False,
    ),
]

# Use the below functions in case data has to be manipulated after the data has been read.
# Use the customPrepareDataPre function in case the time/date data has to be manipulated.
# Use the customPrepareDataPost function in all other cases


# Prepare the input data (before date/time manipulation)
def customPrepareDataPre(dataFrame: pd.DataFrame) -> pd.DataFrame:
    return dataFrame


# Prepare the input data (after date/time manipulation)
def customPrepareDataPost(dataFrame: pd.DataFrame) -> pd.DataFrame:
    # Default no manipulation, add code if needed

    # Example:
    #   dataFrame["Energy Produced (Wh)"] =
    #       dataFrame["Energy Produced (Wh)"].str.replace(',', '').replace('\"', '').astype(int)
    return dataFrame


# ---------------------------------------------------------------------------------------------------------------------

# Template version number
versionNumber = "1.8.1"


# Prepare the input data
def prepareData(dataFrame: pd.DataFrame) -> pd.DataFrame:
    print("Preparing data")

    # Handle any custom dataframe manipulation (Pre)
    dataFrame = customPrepareDataPre(dataFrame)

    # Check if we have to combine a date and time field
    if inputFileTimeColumnName != "":
        # Take note that the format is changed in case the column was parsed as date.
        # For excel change the type of the cell to text or adjust the format accordingly,
        # use statement print(dataFrame) to get information about the used format.
        dataFrame[dateTimeColumnName] = pd.to_datetime(
            dataFrame[inputFileDateColumnName].astype(str)
            + " "
            + dataFrame[inputFileTimeColumnName].astype(str),
            format=inputFileDateTimeColumnFormat,
            utc=True,
        )
    else:
        dataFrame[dateTimeColumnName] = pd.to_datetime(
            dataFrame[inputFileDateColumnName],
            format=inputFileDateTimeColumnFormat,
            utc=True,
        )
    # Remove the timezone (if it exists)
    dataFrame[dateTimeColumnName] = dataFrame[dateTimeColumnName].dt.tz_localize(None)

    # Select only correct dates
    df = dataFrame.loc[
        (dataFrame[dateTimeColumnName] >= datetime.datetime(1970, 1, 1))
        & (dataFrame[dateTimeColumnName] <= datetime.datetime(2099, 12, 31))
    ]

    # Make sure that the data is correctly sorted
    df.sort_values(by=dateTimeColumnName, ascending=True, inplace=True)

    # Transform the date into unix timestamp for Home-Assistant
    df[dateTimeColumnName] = (df[dateTimeColumnName].astype("datetime64[ns]")).astype(
        "int64"
    ) // 10**9

    # Handle any custom dataframe manipulation (Post)
    df = customPrepareDataPost(df)

    return df


# Filter the data based on the provided dataFilter(s)
def filterData(dataFrame: pd.DataFrame, filters: List[DataFilter]) -> pd.DataFrame:
    df = dataFrame
    # Iterate all the provided filters
    for dataFilter in filters:
        # Determine the subset based on the provided filter (regular expression)
        series = (
            df[dataFilter.column].astype(str).str.contains(dataFilter.value, regex=True)
        )

        # Validate whether the data is included or excluded
        if not dataFilter.equal:
            series = ~series

        df = df[series]

    return df


# Recalculate the data so that the value increases
# The value is currently the usage in that interval. This can be used to generate fake "states".
def recalculateData(
    dataFrame: pd.DataFrame, dataColumnName: str | int, initialValue: float
) -> pd.DataFrame:
    # Work on a copy to ensure we're not modifying a slice of the original DataFrame
    df = dataFrame.copy()

    # If the DataFrame is empty, return it as is.
    if df.empty:
        return df

    # 1) Replace NaNs with 0, compute cumulative sum, then add the baseline (initial value)
    cumulative_values = (
        df[dataColumnName].fillna(0).cumsum().add(float(initialValue)).round(3)
    )

    # 2) Shift down so that the first recorded value is exactly initialValue
    df[dataColumnName] = cumulative_values.shift(1, fill_value=initialValue)

    # Calculate the interval between timestamps (first two rows)
    interval = (
        df[dateTimeColumnName].iloc[1] - df[dateTimeColumnName].iloc[0]
        if len(df) >= 2
        else 0
    )

    # Create an extra row:
    # - dateTimeColumnName: last timestamp + interval
    # - value: final cumulative sum value from the original cumulative calculation (including baseline)
    extra_row = {
        dateTimeColumnName: df[dateTimeColumnName].iloc[-1] + interval,
        dataColumnName: cumulative_values.iloc[-1],
    }

    # Append the extra row to the DataFrame
    df = pd.concat([df, pd.DataFrame([extra_row])], ignore_index=True)

    return df


# Generate the datafile which can be imported
def generateImportDataFile(
    dataFrame: pd.DataFrame,
    outputFile: str,
    dataColumnName: str | int,
    filters: list[DataFilter],
    recalculate: bool,
    initialValue: float,
):
    # Check if the column exists
    if dataColumnName not in dataFrame.columns:
        print(
            f"Could not create file: {outputFile} because column: {dataColumnName} does not exist"
        )
        return

    # Column exists, continue
    print("Creating file: " + outputFile)
    dataFrameFiltered = filterData(dataFrame, filters)

    # Check if we have to recalculate the data
    if recalculate:
        dataFrameFiltered = recalculateData(
            dataFrameFiltered, dataColumnName, initialValue
        )

    # Select only the needed data
    dataFrameFiltered = dataFrameFiltered.filter([dateTimeColumnName, dataColumnName])

    if inputFileDateTimeOnlyUseHourly:
        # Floor each timestamp to the start of its hour.
        # For instance, all readings with a timestamp in [16:00, 17:00) become 16:00.
        dataFrameFiltered[dateTimeColumnName] = dataFrameFiltered[
            dateTimeColumnName
        ].apply(lambda x: (x // 3600) * 3600)

        # Group by the floored hourly timestamp and select the first reading in each group.
        dataFrameFiltered = dataFrameFiltered.groupby(
            dateTimeColumnName, as_index=False
        )[dataColumnName].first()

    # Create the output file
    dataFrameFiltered.to_csv(
        outputFile,
        sep=",",
        decimal=".",
        header=False,
        index=False,
        encoding="utf-8",
    )


# Read the inputfile
def readInputFile(inputFileName: str) -> pd.DataFrame:
    # Read the specified file
    print(f"Loading data: {inputFileName}")

    try:
        # Check if we have a supported extension
        if inputFileNameExtension == ".csv":
            # Read the CSV file
            df = pd.read_csv(
                inputFileName,
                sep=inputFileDataSeparator,
                decimal=inputFileDataDecimal,
                skiprows=inputFileNumHeaderRows,
                skipfooter=inputFileNumFooterRows,
                index_col=False,
                na_values=["N/A"],
                header="infer" if inputFileHasHeaderNameRow else None,
                engine="python",
            )
        elif (inputFileNameExtension == ".xlsx") or (inputFileNameExtension == ".xls"):
            # Read the XLSX/XLS file
            warnings.filterwarnings(
                "ignore",
                message="Workbook contains no default style, apply openpyxl's default",
            )
            df = pd.read_excel(
                inputFileName,
                sheet_name=inputFileExcelSheetName,
                decimal=inputFileDataDecimal,
                skiprows=inputFileNumHeaderRows,
                skipfooter=inputFileNumFooterRows,
            )
        elif inputFileNameExtension == ".json":
            # Read the JSON file
            with open(inputFileName, "r", encoding="utf-8") as f:
                jsonData = json.load(f)
            df = pd.json_normalize(jsonData, record_path=inputFileJsonPath)
        elif inputFileNameExtension == ".db":
            # Read the SQLite database file
            conn = sqlite3.connect(inputFileName)
            query = f"SELECT * FROM {inputFileDbTableName}"
            df = pd.read_sql_query(query, conn)
            conn.close()
        else:
            raise Exception(f"Unsupported extension: {inputFileNameExtension}")

        return df
    except Exception as e:
        print(f"Error reading file {inputFileName}: {e}")
        sys.exit(1)


# Check if all the provided files have the correct extension
def correctFileExtensions(fileNames: list[str]) -> bool:
    # Check all filenames for the right extension
    for fileName in fileNames:
        _, fileNameExtension = os.path.splitext(fileName)
        if fileNameExtension != inputFileNameExtension:
            return False
    return True


# Generate the datafiles which can be imported
def generateImportDataFiles(inputFileNames: str, outputFileName: str | None = None):
    # Find the file(s)
    fileNames = glob.glob(inputFileNames)
    if not fileNames:
        print(f"No files found based on: {inputFileNames}")
        return

    print(f"Found {len(fileNames)} files based on: {inputFileNames}")

    if not correctFileExtensions(fileNames):
        print(f"Only {inputFileNameExtension} data files are allowed.")
        return

    # For SQLite .db files, enforce that only one file is allowed.
    if inputFileNameExtension == ".db" and len(fileNames) > 1:
        print("Error: Only one SQLite database file is allowed for .db files.")
        return

    # Read all the found files and concat the data
    dataFrame = pd.concat(map(readInputFile, fileNames), ignore_index=True, sort=True)

    # Prepare the data
    dataFrame = prepareData(dataFrame)

    # Create the output files
    for outputFile in outputFiles:
        # Check if we have to generate a specific output file
        if outputFileName is None or outputFile.outputFileName == outputFileName:
            # Generate the import data file and ensure dataFrame is not modified between definitions
            generateImportDataFile(
                dataFrame.copy(),
                outputFile.outputFileName,
                outputFile.valueColumnName,
                outputFile.dataFilters,
                outputFile.recalculate,
                outputFile.initialValue,
            )
    print("Processing complete.")


# Validate that the script is started from the command prompt
if __name__ == "__main__":
    print(f"{energyProviderName} Data Prepare\n")
    print(
        f"This python script prepares {energyProviderName} data for import into Home Assistant.\n"
    )
    parser = argparse.ArgumentParser(
        description=f"""
Notes:
- Enclose the path/filename in quotes in case wildcards are being used on Linux-based systems.
- Example: {energyProviderName}DataPrepare "*{inputFileNameExtension}"
    """,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Automatically answer yes to any prompts",
    )

    parser.add_argument(
        "input_file",
        type=str,
        help=f"Path to the {energyProviderName} {inputFileNameExtension} file(s) (supports wildcards).",
    )

    parser.add_argument(
        "output_file",
        nargs="?",
        type=str,
        default=None,
        help="Optional: Name of the specific output file to generate (default: all).",
    )

    args = parser.parse_args()

    print(
        "The files will be prepared in the current directory. Any previous files will be overwritten!\n"
    )

    # proceed automatically if --yes was passed
    if args.yes or (
        input("Are you sure you want to continue [Y/N]?: ")
        .strip()
        .lower()
        .startswith("y")
    ):
        generateImportDataFiles(args.input_file, args.output_file)
