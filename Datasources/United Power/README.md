# Energy provider: United Power

United Power offers the option to export data from the [United Power](https://www.unitedpower.com/) website. This data can be transformed and used to import into Home Assistant.

**Data provided**

- Electricity consumption - Tariff 1 - High resolution (hourly or daily interval) - kWh
- Electricity feed-in (solar export) - Tariff 1 - High resolution (hourly or daily interval) - kWh

**Supported export formats:**

- **CSV Format**: Green Button CSV with time period ranges (recommended for compatibility)
- **XML Format**: Green Button XML (ESPI standard) - downloaded as `.xml` or `.zip` file

**Granularity options:**

- **Daily** (available via Web UI): Good for monthly/yearly trends, one reading per day
- **Hourly** (requires API access): Best for detailed analysis, shows hour-by-hour consumption and solar export - not available in web UI, requires manual cURL/API request (see Method 2 below)

**Tooling needed**

- Python 3
- Pandas python library `pip install pandas`
- Tzlocal python library `pip install tzlocal`
- Tzdata python library `pip install tzdata`

**How-to export data from United Power SmartHub**

**Method 1: Daily Data (via Web UI)**

1. Log in to your [United Power SmartHub account](https://unitedpower.smarthub.coop)
2. Navigate to **Usage & Billing** → **Usage Dashboard**
3. Select the date range you want to export
4. Click the **Green Button Download** option and choose your format:
   - **CSV Format** (recommended): Downloads as `.csv` file
   - **XML Format**: Downloads as `.zip` file containing XML (ESPI standard)
5. Save the downloaded file

**Method 2: Hourly Data (via API - Advanced)**

The hourly granularity option is not available in the web UI. You need to use the API directly:

1. Log in to your [United Power SmartHub account](https://unitedpower.smarthub.coop) in your browser
2. Open browser Developer Tools (F12) → Network tab
3. Navigate to the Usage Dashboard and download any data export
4. Find the `greenButtonCsvDownload` or `greenButtonDownload` request in the Network tab
5. Copy as cURL (right-click → Copy → Copy as cURL)
6. Modify the URL parameter `timeFrame=Daily` to `timeFrame=Hourly`
7. Run the modified cURL command in your terminal to download the hourly data

Example cURL command structure:

```bash
curl 'https://unitedpower.smarthub.coop/services/secured/greenButtonCsvDownload?account=YOUR_ACCOUNT&serviceLocation=YOUR_LOCATION&timeFrame=Hourly&startDate=START_MS&endDate=END_MS&serviceDesc=ACCOUNT|LOCATION&industry=Electric&userId=your@email.com' \
  -H 'authorization: Bearer YOUR_TOKEN' \
  -H 'x-nisc-smarthub-username: your@email.com'
```

**Note:** Bearer tokens expire after a short time, so you'll need to refresh the token if the API request fails.

**How-to import the data into Home Assistant**

1. Download the `UnitedPowerDataPrepare.py` and the `DataPrepareEngine.py` (from the Datasources directory) files and put them in the same directory as the downloaded United Power data
2. Execute the python script with the name of the file that contains the exported data as parameter:

   ```bash
   # For CSV files
   python UnitedPowerDataPrepare.py united_power_export.csv

   # For XML/ZIP files
   python UnitedPowerDataPrepare.py green_button_data.zip
   ```

3. The python script creates the needed files for the generic import script:
   - `elec_feed_in_tariff_1_high_resolution.csv` - Energy consumption from the grid (cumulative kWh)
   - `elec_feed_out_tariff_1_high_resolution.csv` - Solar energy exported to the grid (cumulative kWh)
4. Follow the steps in the overall how-to to import these files into Home Assistant

**Notes**

- United Power is an electric distribution cooperative serving areas north of Denver, Colorado
- The script is configured for the America/Denver timezone by default
- The script supports both CSV and XML (Green Button ESPI) formats
- **Green Button CSV export format** includes:
  - **Multiple meter readings** in a single file (typically 3-4 phases/meters)
  - The script automatically aggregates these readings into single values per timestamp
  - **Time periods** can be:
    - Daily intervals: `"2025-10-19 00:00 to 2025-10-20 00:00"`
    - Hourly intervals: `"2025-10-19 00:00 to 2025-10-19 01:00"`
  - **Positive values** indicate electricity consumption from the grid
  - **Negative values** indicate solar energy exported to the grid (not total solar production)
- **Green Button XML export format** (ESPI standard):
  - Downloaded as a `.zip` file containing XML and HTML files
  - The script automatically extracts and parses the XML from the ZIP archive
  - Provides the same data as CSV format, structured according to ESPI (Energy Services Provider Interface) standard
  - Multiple IntervalReading entries are aggregated per timestamp
- The script automatically:
  - Separates consumption and export data into separate output files
  - Aggregates multiple meter readings per timestamp (no duplicates)
  - Converts to cumulative kWh format required by Home Assistant
- **Note about solar data**: The export file only shows excess solar energy sent back to the grid, not your total solar production. Solar power consumed directly by your home is not visible in utility data.
- Contact United Power customer service if you need assistance accessing or exporting your energy usage data
