# Energy provider: SMA

SMA offers the option to export data from the SMA device. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Solar production - High resolution (5 min interval) - Wh
- Solar production - Low resolution (day interval) - Wh

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`


**How-to**
- Export data from the SMA device
  - Go to the SMA device web interface
  - Login with your account (installer account or admin account)
  - Go to the `Gegevens` menu item (Dutch) or `Data` menu item (English)
  - Select the type of data that needs to be exported (high resolution - 5 minutes or low resolution - daily)
  - Select the period
  - Click on `Gegevens exporteren` (Dutch) or `Export data` (English)
  - The data for the selected period is downloaded to your PC as a separate file
- Download the `SMADataPrepare.py` and the `DataPrepareEngine.py` (Datasources directory) files and put it in the same directory as the downloaded CSV data
- Execute the python script with as parameter the name of the directory which contains the files with the exported data `python SolarmanDataPrepare.py *.csv elec_solar_high_resolution.csv`.
The python script creates the needed file for the generic import script.
The script can handle both high resolution (5 min interval) and low resolution (day interval) data.
Depending on the data that needs to be imported, the filename of the output file needs to be specified as the last parameter otherwise both output files will be created.
- Follow the steps in the overall how-to

**Optional Step: Provide starting reading**<br>
By default, source data is treated as per-interval usage starting at zero.
When the meter’s initial reading is not zero or readings began after installation, an explicit initial value can be applied.
This step is optional but can prevent a spike at the point where imported data crosses over into existing Home Assistant statistics.
A spike can also be avoided by lowering the `cutoff_invalid_value` in the `Import Energy data into Home Assistant` SQL import script so that it falls below the initial reading.
The summarize: the spike only occurs when the intial reading is lower than the `cutoff_invalid_value`.

1. **Run with zero baseline**<br>
   Execute the script to generate the CSV file(s). The first reading will be treated as zero by default.

2. **Choose a common timestamp**<br> 
   Identify an epoch (first-column timestamp) present in both the exported CSV and Home Assistant’s `statistics` table.

3. **Compare readings**<br>
   - In the CSV, record the cumulative value at that timestamp.
   - In the `statistics` table, locate the row where `start_ts` equals that epoch and note its `state`.

4. **Calculate the baseline**<br>
   ```text
   initialValue = (Home Assistant state) – (exported cumulative at that epoch)
   ```
   For example, if the epoch 1703886300 corresponds to a CSV value of 123.456 and a statistics state of 580.245, then:
   ```text
   initialValue = = 580.245 – 123.456 = 456.789
   ```
5. **Add the `initialValue` parameter and re-run**<br>
   Add the `initialValue=<calculated value>` as the fifth argument in the script’s output definition.
   Execute the script again to regenerate the CSV file(s). Repeat for each output definition.