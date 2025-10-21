# Energy provider: Xcel Energy

Xcel Energy offers the option to export data from the [Xcel Energy](https://www.xcelenergy.com/) website. This data can be transformed and used to import into Home Assistant.

**Data provided**

The script automatically detects what data is available in your export and creates the appropriate output files:

- **Gas only accounts**: Creates `gas_high_resolution.csv` with monthly gas consumption in Therms
- **Electric only accounts**: Creates `elec_feed_in_tariff_1_high_resolution.csv` with monthly electricity consumption in kWh
- **Dual service accounts** (both gas and electric): Creates both output files

Note: For more granular electricity data, Green Button export may provide interval data if you have a smart meter

**Tooling needed**

- Python 3
- Pandas python library `pip install pandas`
- Tzlocal python library `pip install tzlocal`
- Tzdata python library `pip install tzdata`

**How-to export data from Xcel Energy website**

**Recommended Method: Bill History Export (provides all historical data back to October 2021)**

1. Log in to your [Xcel Energy account](https://my.xcelenergy.com/)
2. Navigate to **My Bill History** at [https://myenergy.xcelenergy.com/myenergy/bill-presentment](https://myenergy.xcelenergy.com/myenergy/bill-presentment)
3. Click **"Display All Bills"** to show all available billing history
4. Click **"Export"** button to download the complete bill history as CSV
   - The exported CSV will contain all available data (typically back to October 2021)
   - Includes: Bill Date, Gas Usage (Therms), Gas Charges ($)
   - If you have electric service, it will also include Electric Usage (kWh) and Electric Charges ($)
5. Save the downloaded file (usually named "Premise summary MM-DD-YYYY.csv")

**Alternative Method: Usage Chart (provides only last 13 months)**

1. Log in to your [Xcel Energy account](https://my.xcelenergy.com/)
2. Click on **"Usage"** → **"VISIT MY ENERGY"** → **"View My Usage & Cost"**
3. Click on **"Chart Download"** → **"Download CSV"**
4. Note: This method only exports the most recent 13 months of data

**How-to import the data into Home Assistant**

1. Download the `XcelEnergyDataPrepare.py` and the `DataPrepareEngine.py` (from the Datasources directory) files and put them in the same directory as the downloaded Xcel Energy CSV data
2. Execute the python script with the name of the file that contains the exported data as parameter:
   ```bash
   python XcelEnergyDataPrepare.py "Premise summary MM-DD-YYYY.csv"
   ```
3. The python script will automatically detect whether you have gas, electric, or both services and create the appropriate output files:
   - `gas_high_resolution.csv` (if gas data is present)
   - `elec_feed_in_tariff_1_high_resolution.csv` (if electric data is present)
4. Follow the steps in the overall how-to to import the data into Home Assistant

**Notes**

- Xcel Energy operates in multiple states (Colorado, Michigan, Minnesota, New Mexico, North Dakota, South Dakota, Texas, and Wisconsin)
- **Historical Data Availability**: Xcel Energy's online portal only maintains billing history back to **October 2021**. Earlier data is not available for export.
- The CSV export provides monthly billing cycle usage data (not daily or hourly intervals)
- The data export format may vary slightly depending on your state/region and meter type
- If you have both electric and gas meters, the Bill History export will include both in the same CSV file
- The script assumes the timezone is set to your local timezone - adjust `inputFileTimeZoneName` if needed
- **Green Button**: Xcel Energy supports Green Button data export for **electricity only** (not available for gas meters). Green Button may provide more detailed interval data if you have a smart meter. For gas usage, you must use the CSV export method described above.

**Alternative: API Access**

- **Note**: Programmatic API access to Xcel Energy is not currently feasible. The unofficial `pyxcel` Python library is outdated and no longer works with the current Xcel Energy website (which now uses Salesforce Aura framework). Manual CSV export is the recommended approach.
