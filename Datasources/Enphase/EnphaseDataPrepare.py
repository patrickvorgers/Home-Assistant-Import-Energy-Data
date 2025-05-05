import sys
from pathlib import Path

import pandas as pd

# 1) Add engine to path (simple way to add the engine to the path)
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# 2) Import engine (supress linter warnings)
import DataPrepareEngine as engine # noqa: E402
from DataPrepareEngine import OutputFileDefinition # noqa: E402

# 3) Override DataPrepare engine globals
# Name of the energy provider
engine.energyProviderName = "Enphase"

# Inputfile(s): filename extension
engine.inputFileNameExtension = ".csv"
# Inputfile(s): Name of the column containing the date of the reading.
#               Use this in case date and time is combined in one field.
#               Use the numerical column index in case the column name is not available.
engine.inputFileDateColumnName = "Date/Time"
# Inputfile(s): Date/time format used in the datacolumn.
#               Combine the format of the date and time in case date and time are two seperate fields.
engine.inputFileDateTimeColumnFormat = "%m/%d/%Y %H:%M"
# Inputfile(s): Data separator being used in the input file (only csv files)
engine.inputFileDataSeparator = ","
# Inputfile(s): Decimal token being used in the input file (csv and excel files)
engine.inputFileDataDecimal = "."
# Inputfile(s): Whether the input file has a header row from which header names can be derived (only csv files)
engine.inputFileHasHeaderNameRow = True
# Inputfile(s): Number of header rows in the input file (csv and excel files)
engine.inputFileNumHeaderRows = 0
# Inputfile(s): Number of footer rows in the input file (csv and excel files)
engine.inputFileNumFooterRows = 1

# List of one or more output file definitions
engine.outputFiles = [
    OutputFileDefinition(
        "elec_feed_in_tariff_1_high_resolution.csv",
        "Imported from Grid (Wh)",
        [],
        True,
    ),
    OutputFileDefinition(
        "elec_feed_out_tariff_1_high_resolution.csv",
        "Exported to Grid (Wh)",
        [],
        True,
    ),
    OutputFileDefinition(
        "elec_solar_high_resolution.csv",
        "Energy Produced (Wh)",
        [],
        True,
    ),
]
# Use this output file definitions in case separate tariffs are needed
# engine.outputFiles = [
#     OutputFileDefinition(
#         "elec_feed_in_tariff_1_high_resolution.csv",
#         "Imported from Grid (Wh)",
#         [DataFilter('Tariff', '1', True)],
#         True,
#     ),
#     OutputFileDefinition(
#         "elec_feed_in_tariff_2_high_resolution.csv",
#         "Imported from Grid (Wh)",
#         [DataFilter('Tariff', '2', True)],
#         True,
#     ),
#     OutputFileDefinition(
#         "elec_feed_out_tariff_1_high_resolution.csv",
#         "Exported to Grid (Wh)",
#         [DataFilter('Tariff', '1', True)],
#         True,
#     ),
#     OutputFileDefinition(
#         "elec_feed_out_tariff_2_high_resolution.csv",
#         "Exported to Grid (Wh)",
#         [DataFilter('Tariff', '2', True)],
#         True,
#     ),
#     OutputFileDefinition(
#         "elec_solar_high_resolution.csv",
#         "Energy Produced (Wh)",
#         [],
#         True,
#     ),
# ]


# Prepare the input data (after date/time manipulation)
def customPrepareDataPost(dataFrame: pd.DataFrame) -> pd.DataFrame:
    if dataFrame["Energy Produced (Wh)"].dtype == "object":
        dataFrame["Energy Produced (Wh)"] = (
            dataFrame["Energy Produced (Wh)"]
            .str.replace(",", "")
            .replace('"', "")
            .astype(int)
        )
    if ("Exported to Grid (Wh)" in dataFrame.columns) and (
        dataFrame["Exported to Grid (Wh)"].dtype == "object"
    ):
        dataFrame["Exported to Grid (Wh)"] = (
            dataFrame["Exported to Grid (Wh)"]
            .str.replace(",", "")
            .replace('"', "")
            .astype(int)
        )
    if ("Imported from Grid (Wh)" in dataFrame.columns) and (
        dataFrame["Imported from Grid (Wh)"].dtype == "object"
    ):
        dataFrame["Imported from Grid (Wh)"] = (
            dataFrame["Imported from Grid (Wh)"]
            .str.replace(",", "")
            .replace('"', "")
            .astype(int)
        )

    # Create a tariff column, uncomment the below lines if needed
    # for index, _ in dataFrame.iterrows():
    #    recordDateTime = pd.to_datetime(dataFrame.at[index, dateTimeColumnName], unit='s')
    #    # Check if it is Monday, Tuesday, Wednesday, Thursday or Friday
    #    if recordDateTime.weekday() in [0, 1, 2, 3, 4, 5]:
    #        # Check if we are between 00:00-6:59 and 23:00-23:59
    #        if ((recordDateTime.time() < time(7,0)) or (recordDateTime.time() >= time(23,0))):
    #            # Low tariff
    #            dataFrame.at[index, 'Tariff'] = 2
    #        else:
    #            # High tariff
    #            dataFrame.at[index, 'Tariff'] = 1
    #    else:
    #        # Low tariff
    #        dataFrame.at[index, 'Tariff'] = 2
    return dataFrame


# 4) Invoke DataPrepare engine
if __name__ == '__main__':
    # Set the hook functions
    engine.customPrepareDataPost = customPrepareDataPost

    engine.main()
