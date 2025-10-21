import os
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime
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
engine.energyProviderName = "United Power"

# Inputfile(s): filename extension (supports CSV, XML, and ZIP)
engine.inputFileNameExtension = [".csv", ".xml", ".zip"]
# Inputfile(s): Name of the column containing the date of the reading.
#               Use this in case date and time is combined in one field.
#               Use the numerical column index in case the column name is not available.
engine.inputFileDateColumnName = "DateTime"
# Inputfile(s): Date/time format used in the datacolumn.
#               Combine the format of the date and time in case date and time are two seperate fields.
engine.inputFileDateTimeColumnFormat = "%Y-%m-%d %H:%M"
# Inputfile(s): Date/time UTC indication
#               Set to True in case the date/time is in UTC, False in case it is in local time.
engine.inputFileDateTimeIsUTC = False
# Inputfile(s): Name of the timezone of the input data
#               The IANA timezone name of the input data (so that DST can be correctly applied).
#               Example: "Europe/Amsterdam", "America/New_York".
#               Leave as empty string to auto-detect from the local machine.
#               Setting is only needed when the setting inputFileDateTimeIsUTC is False.
engine.inputFileTimeZoneName = "America/Denver"
# Inputfile(s): Data separator being used in the input file (only csv files)
engine.inputFileDataSeparator = ","
# Inputfile(s): Decimal token being used in the input file (csv and excel files)
engine.inputFileDataDecimal = "."
# Inputfile(s): Whether the input file has a header row from which header names can be derived (only csv files)
engine.inputFileHasHeaderNameRow = False
# Inputfile(s): Number of header rows in the input file (csv and excel files)
engine.inputFileNumHeaderRows = 0
# Inputfile(s): Number of footer rows in the input file (csv and excel files)
engine.inputFileNumFooterRows = 0

# List of one or more output file definitions
# United Power provides consumption (positive) and feed-in (negative values)
engine.outputFiles = [
    OutputFileDefinition(
        "elec_feed_in_tariff_1_high_resolution.csv",
        "Consumption",
        [],
        IntervalMode.USAGE,
    ),
    OutputFileDefinition(
        "elec_feed_out_tariff_1_high_resolution.csv",
        "FeedIn",
        [],
        IntervalMode.USAGE,
    ),
]


def parse_xml_green_button(xml_content: str) -> pd.DataFrame:
    """
    Parse Green Button XML format (ESPI - Energy Services Provider Interface).

    The XML contains IntervalBlock entries with IntervalReading elements.
    Each reading has a timestamp, duration, value, and powerOfTenMultiplier.
    """
    rows = []

    # Parse XML
    root = ET.fromstring(xml_content)

    # Define namespaces
    ns = {"atom": "http://www.w3.org/2005/Atom", "espi": "http://naesb.org/espi"}

    # Find all IntervalBlock entries
    for entry in root.findall(".//atom:entry", ns):
        content = entry.find("atom:content", ns)
        if content is None:
            continue

        interval_block = content.find("espi:IntervalBlock", ns)
        if interval_block is None:
            continue

        # Parse each IntervalReading
        for reading in interval_block.findall("espi:IntervalReading", ns):
            time_period = reading.find("espi:timePeriod", ns)
            if time_period is None:
                continue

            start_elem = time_period.find("espi:start", ns)
            value_elem = reading.find("espi:value", ns)

            if start_elem is None or value_elem is None:
                continue

            # Extract values
            timestamp = int(start_elem.text) if start_elem.text else 0
            raw_value = int(value_elem.text) if value_elem.text else 0

            # The value is in Wh (watt-hours), convert to kWh
            # powerOfTenMultiplier indicates the scale but values are already in base unit
            value = raw_value / 1000.0  # Convert Wh to kWh

            # Convert timestamp to datetime string
            dt = datetime.fromtimestamp(timestamp)
            datetime_str = dt.strftime("%Y-%m-%d %H:%M")

            # Split into consumption and feed-in
            consumption = max(0, value)
            feed_in = abs(min(0, value))

            rows.append(
                {
                    "DateTime": datetime_str,
                    "Consumption": consumption,
                    "FeedIn": feed_in,
                }
            )

    if rows:
        df = pd.DataFrame(rows)

        # Aggregate multiple readings for the same datetime
        df = df.groupby("DateTime", as_index=False).agg(
            {"Consumption": "sum", "FeedIn": "sum"}
        )

        # Sort by datetime
        df = df.sort_values("DateTime").reset_index(drop=True)

        return df
    else:
        return pd.DataFrame(columns=["DateTime", "Consumption", "FeedIn"])


# Custom file reader for United Power's unique format
def customReadInputFile(inputFileName: str) -> pd.DataFrame:
    """
    Custom file reader for United Power Green Button data which supports:

    **CSV Format:**
    - Multiple header sections
    - Time period ranges like "2025-10-01 00:00 to 2025-10-02 00:00"
    - Multiple meter readings per time period (typically 3-4 phases/meters)
    - Inconsistent column counts (can't be parsed by pandas directly)

    **XML Format (Green Button ESPI):**
    - Standard Green Button XML with IntervalBlock entries
    - Can be provided as raw .xml or .zip file

    Supports both daily and hourly granularity exports:
    - Daily: Each time period is 24 hours (e.g., "2025-10-19 00:00 to 2025-10-20 00:00")
    - Hourly: Each time period is 1 hour (e.g., "2025-10-19 00:00 to 2025-10-19 01:00")

    The function aggregates multiple meter readings for the same timestamp,
    splitting positive values (grid consumption) and negative values (solar export).
    """
    print(f"Loading data: {inputFileName}")

    # Determine file type
    file_ext = Path(inputFileName).suffix.lower()

    # Handle ZIP files (extract XML and process)
    if file_ext == ".zip":
        print("Detected ZIP file, extracting XML...")
        with zipfile.ZipFile(inputFileName, "r") as zip_ref:
            # Find XML file in the zip
            xml_files = [f for f in zip_ref.namelist() if f.endswith(".xml")]
            if not xml_files:
                raise ValueError(f"No XML file found in {inputFileName}")

            # Read the first XML file
            xml_filename = xml_files[0]
            print(f"Processing {xml_filename} from archive...")
            with zip_ref.open(xml_filename) as xml_file:
                xml_content = xml_file.read().decode("utf-8")
                return parse_xml_green_button(xml_content)

    # Handle XML files
    elif file_ext == ".xml":
        print("Detected XML file...")
        with open(inputFileName, "r", encoding="utf-8") as f:
            xml_content = f.read()
            return parse_xml_green_button(xml_content)

    # Handle CSV files (original logic)
    print("Detected CSV file...")
    rows = []

    # Read the file as text
    with open(inputFileName, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Parse each line
    for line in lines:
        line = line.strip()

        # Skip header lines and empty lines
        if (
            "========================================" in line
            or "Usage Information" in line
            or "For:" in line
            or "Meter Reading Information" in line
            or "Type of readings:" in line
            or "Detailed Usage" in line
            or "Start date:" in line
            or "Interval Blockdata" in line
            or "Energy consumption time period" in line
            or line == ""
        ):
            continue

        # Check if this is a data row (contains "to" indicating time range)
        if " to " in line:
            try:
                # Parse: "2025-10-01 00:00 to 2025-10-02 00:00,-26.370,,"
                parts = line.split(",")
                if len(parts) >= 2:
                    time_period = parts[0].strip()
                    usage_value = parts[1].strip()

                    # Skip if usage value is empty
                    if not usage_value:
                        continue

                    # Extract start datetime from time period
                    if " to " in time_period:
                        start_datetime = time_period.split(" to ")[0].strip()
                    else:
                        continue

                    # Parse usage value
                    try:
                        usage = float(usage_value)
                    except ValueError:
                        continue

                    # Split usage into consumption (positive) and feed-in (negative converted to positive)
                    consumption = max(0, usage)  # Keep positive values
                    feed_in = abs(min(0, usage))  # Convert negative to positive

                    rows.append(
                        {
                            "DateTime": start_datetime,
                            "Consumption": consumption,
                            "FeedIn": feed_in,
                        }
                    )
            except Exception:
                # Skip rows that can't be parsed
                continue

    # Create dataframe from parsed rows
    if rows:
        df = pd.DataFrame(rows)

        # Aggregate multiple readings for the same datetime (sum them up)
        # This handles cases where there are multiple meter readings per time period
        df = df.groupby("DateTime", as_index=False).agg(
            {"Consumption": "sum", "FeedIn": "sum"}
        )

        # Sort by datetime to ensure chronological order
        df = df.sort_values("DateTime").reset_index(drop=True)

        return df
    else:
        # Return empty dataframe with expected columns if no data found
        return pd.DataFrame(columns=["DateTime", "Consumption", "FeedIn"])


# 4) Invoke DataPrepare engine
if __name__ == "__main__":
    # Override the file reading function with our custom parser
    engine.readInputFile = customReadInputFile

    # Override the file extension validation to support multiple extensions
    original_correctFileExtensions = engine.correctFileExtensions

    def correctFileExtensions_multi(fileNames: list[str]) -> bool:
        """Modified version that supports multiple file extensions"""
        allowed_extensions = engine.inputFileNameExtension
        if isinstance(allowed_extensions, str):
            allowed_extensions = [allowed_extensions]

        for fileName in fileNames:
            _, fileNameExtension = os.path.splitext(fileName)
            if fileNameExtension not in allowed_extensions:
                return False
        return True

    engine.correctFileExtensions = correctFileExtensions_multi

    engine.main()
