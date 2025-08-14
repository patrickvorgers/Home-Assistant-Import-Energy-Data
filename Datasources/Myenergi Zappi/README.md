# Energy provider: Myenergi Zappi (Smart EV charger)

Myenergi Zappi (Smart EV charger) offers the option to export data from the [Myenergi](https://www.myenergi.com/) site. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Electricity import meter - High resolution (hour interval) - Wh

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`
- Tzlocal python library `pip install tzlocal`

**Help needed**

Currently, the script supports the Zappi device, which is a Smart EV charger from Myenergi.
Myenergi also offers other devices like Libbi (Homebattery).
To support these devices, the script may need adjustments to handle different data formats or additional fields.
If you have other Myenergi devices, it would be helpful to provide sample data for those devices so support can be added to the script.

**How-to**
- Export data from the [Myenergi](https://www.myenergi.com/) site
  - Go to the [Myenergi login](https://myaccount.myenergi.com/login) site and login with your account
  - On the left menu, go to *Data reports*
  - Select the device you wish to export (i.e. Zappi)
  - Click "Show More" and Select `Diverter Energy (L1) (Wh)`, `Diverter Energy (L2) (Wh)` and `Diverter Energy (L3) (Wh)`
  - Select the period you wish to export
  - Check your Email Address and click *Send Email*. Within 15 minutes you will get an Email with a link to download the export
  - Open the email and click the link to download the generated CSV file to your PC
- Download the `MyenergiZappiDataPrepare.py` and the `DataPrepareEngine.py` (Datasources directory) files and put it in the same directory as the Myenergi Zappi data
- Execute the python script with as parameter the name of the file that contains the exported data `python MyenergiZappiDataPrepare.py XXXXXXXX_zappi_report.csv`. The python script creates the needed files for the generic import script.
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