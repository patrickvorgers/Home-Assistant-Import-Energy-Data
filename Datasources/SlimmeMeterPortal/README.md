# Energy provider: Slimme Meter Portal

The SlimmeMeterPortal offers the option to export data from the SlimmeMeterPortal site. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (15 min interval) - kWh
- Electricity consumption - Tariff 2 - High resolution (15 min interval) - kWh
- Electricity production - Tariff 1 - High resolution (15 min interval) - kWh
- Electricity production - Tariff 2 - High resolution (15 min interval) - kWh
- Gas consumption - High resolution (hour interval) - m³

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`
- OpenPyXL python library `pip install openpyxl`

**How-to**
- Export data from the [Slimme Meter Portal](https://www.slimmemeterportal.nl/) site
  - Go to the [Slimme Meter Portal](https://www.slimmemeterportal.nl/) site
  - Click on `Inloggen`
  - Provide `E-mailadres` and `Wachtwoord` and click on `INLOGGEN`
  - Hover over `PlusAccount` and select `Detaildata Downloaden`
  - Repeat the below steps for all the needed meters and years
      - Select the meter and year and click on `BESTAND OPVRAGEN`
      - Download the generated file
- Download the `SlimmeMeterPortalDataPrepare.py` and/or `SlimmeMeterPortalGasDataPrepare.py` and the `DataPrepareEngine.py` (Datasources directory) files and put it in the same directory as the Slimme Meter Portal data
- Execute the python script with as parameter the name of the file that contains the exported data `python SlimmeMeterPortalDataPrepare.py data_20??_871687120058657526.xlsx`.
  The python script creates the needed files for the generic import script.
  To import data for multiple years, use `?` or `*` in the filename to match multiple files.
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