# Energy provider: NEM12

NEM12 is a standard for Australian smart meter data, it allows users to export their electricity consumption data, which can be processed and imported into Home Assistant.
This implementation is based on the NEM12 standard, which is used by many Australian energy providers.
It does not fully implement the NEM12 standard, but it tries to extract the data from the NEM12 records.
This implementation is under development and may not work for all NEM12 files.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (hour interval) - kWh
- Electricity production - Tariff 1 - High resolution (hour interval) - kWh

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`

**How-to**
- Export your electricity consumption data in the NEM12 format.
- Download the `NEM12DataPrepare.py` script and place it in the same directory as the exported NEM12 data.
- Execute the Python script by providing the name of the exported file as a parameter. Example:  
  `python NEM12DataPrepare.py power-redacted.csv`.  
  The script will generate the necessary files for importing the data into Home Assistant.
- Follow the steps in the overall Home Assistant import guide for integrating the data into your setup.

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