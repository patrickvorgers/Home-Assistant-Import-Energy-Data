# Energy provider: Zonneplan

Zonneplan does not directly provide the possibility to export data. Data can be requested by sending an email to Zonneplan. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (hour interval) - kWh
- Electricity production - Tariff 1 - High resolution (hour interval) - kWh
- Gas consumption - High resolution (hour interval) - m³

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`
- Tzlocal python library `pip install tzlocal`
- OpenPyXL python library `pip install openpyxl`

**How-to**
- Request the data from [Zonneplan](https://www.zonneplan.nl/)
  - Go to the [Zonneplan](https://www.zonneplan.nl/) site
  - Click on `Service`
  - Request via the chatbot to be connected with an employee
  - Request from the employee the data
- Download the `ZonneplanDataPrepare.py` and the `DataPrepareEngine.py` (Datasources directory) files and put it in the same directory as the Zonneplan data
- Execute the python script with as parameter the name of the file that contains the exported data `python ZonneplanDataPrepare.py export-2025-01-21.11_17_12.xlsx`.
  The python script creates the needed files for the generic import script.
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