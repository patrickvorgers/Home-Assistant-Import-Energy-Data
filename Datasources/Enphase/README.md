# Energy provider: Enphase

Enphase offers the option to export data from the [Enlighten Enphase Energy](https://enlighten.enphaseenergy.com/) site. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (hour interval) - kWh (Metered version)
- Electricity production - Tariff 1 - High resolution (hour interval) - kWh (Metered version)
- Solar production - High resolution (hour interval) - Wh

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`
- Tzlocal python library `pip install tzlocal`

**How-to**
- Export data from the [Enlighten Enphase Energy](https://enlighten.enphaseenergy.com/) site
  - Go to the [Enlighten Enphase Energy](https://enlighten.enphaseenergy.com/) site
  - Set the language to English (bottom right corner)
      - Goto account and set the language to English in case the language is not set correctly during logon
  - Login with your account
  - Follow the below substeps in case you have access to the installer version of the site (orange layout)
    - Select your system
    - In the site menu select 'MyEnphase View'
    - Go to the new tab that has been opened with the 'customer' view (blue layout)
  - Select the 'Hamburger icon' in the top right corner (three lines)
  - Select 'System'
  - Select 'Reports'
  - In the top dropdown select 'Custom' (scroll down in the dropdown to find the report)
  - Select the data type: 'Produced' and if available 'Imported/Exported' (Metered version)
  - Choose the data frequency: 1 hour
  - Fill in the start and end date of the report and press 'Email Report'
  - After the report has been generated the CSV is emailed to the registerd emailadress
  - Open the email and download the generated CSV file to your PC
- Download the `EnphaseDataPrepare.py` and the `DataPrepareEngine.py` (Datasources directory) files and put it in the same directory as the Enphase data
- Execute the python script with as parameter the name of the file that contains the exported data `python EnphaseDataPrepare.py 9999999_site_energy_production_report.csv`. The python script creates the needed files for the generic import script.
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