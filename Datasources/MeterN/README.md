# Energy provider: MeterN

MeterN is a lightweight set of PHP/JS files that makes a Home energy metering & monitoring solution (see [MeterN site](https://github.com/jeanmarc77/meterN) for more information).
It offers the option to export the data of each tracked energymeter in a CSV file. This data can be transformed and used to import into Home Assistant.

![meterN demo](https://filedn.eu/lA1ykXBhnSe0rOKmNzxOM2H/images/mN/mn_ss.png)

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (day interval) - kWh
- Electricity production - Tariff 1 - High resolution (day interval) - kWh
- Solar production - High resolution (day interval) - kWh
- Gas consumption - High resolution (day interval) - m³
- Water consumption - High resolution (day interval) - m³

MeterN also provides the option to track additional energy consumption for example, that of electric cars.
This data can be exported and imported into Home Assistant using a simple trick.
For instance, it can be transformed into a dummy solar import file (`elec_solar_high_resolution.csv`).
By using this file and adjusting the `sensor_id_elec_solar` in the import script to match the correct sensor ID for the electric car, the data can be imported into Home Assistant.

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`

**How-to**
- Export data from your local MeterN site
- Download the `MeterNDataPrepare.py` and the `DataPrepareEngine.py` (Datasources directory) files and put it in the same directory as the downloaded MeterN data
- Execute the python script with as parameter the name of the file that contains the exported data **and** the output file that needs to be generated. The python script creates the needed files for the generic import script.
    - `python3 MeterNDataPrepare.py 1FV_Totale20??.csv elec_solar_high_resolution.csv`
    - `python3 MeterNDataPrepare.py 7Prelievi20??.csv elec_feed_in_tariff_1_high_resolution.csv`
    - `python3 MeterNDataPrepare.py 8Immissioni20??.csv elec_feed_out_tariff_1_high_resolution.csv`
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
