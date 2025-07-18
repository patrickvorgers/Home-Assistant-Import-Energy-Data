# Energy provider: Fluvius

Fluvius offers the option to export data from the [Mijn Fluvius](https://mijn.fluvius.be/) site. This data can be transformed and used to import into Home Assistant.

It is recommended to create a quarter hourly (15 minute) export request so you can export the quarter hourly totals.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (15 minute interval) - kWh
- Electricity consumption - Tariff 2 - High resolution (15 minute interval) - kWh
- Electricity production - Tariff 1 - High resolution (15 minute interval) - kWh
- Electricity production - Tariff 2 - High resolution (15 minute interval) - kWh
- Gas consumption - High resolution (hour interval) - m³ or kWh

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`
- Tzlocal python library `pip install tzlocal`

**How-to**

To be able to download quarter hourly CSVs, you need to make a request to be able to download them.

You might also need to enable the P1 port to activate quarter hourly reports on https://mijn.fluvius.be/poortbeheer/

You need to do this only once for each meter.

- Setup the quarter hourly reports (only once per meter)
  - Go to https://mijn.fluvius.be/verbruik/aanvragen 
  - Select the meter and continue to the next page
  - Select "Kwartier" or "Alle" - this allows you to be able to download quarter hourly data and continue to the next page
  - Select "Alle verbruiken vanaf ..." and continue to the next page
  - Confirm the request (you will receive an email to approve the request)

- Export data from the [Mijn Fluvius](https://mijn.fluvius.be/) site
  - Go to https://mijn.fluvius.be/verbruik/
  - For the meter, click *Details* and *Verbruik*, then *Rapport downloaden* and select *kwartiertotalen*.
  - Select the time frame and press *Download*
  - Do the same thing for your Gas Meter if you have one and download it in the same directory
  - Download the `FluviusDataPrepare.py` and the `DataPrepareEngine.py` (Datasources directory) files and put it in the same directory as the Enphase data
  - Execute the python script with as parameter the name of the file that contains the exported data `python FluviusDataPrepare.py "Verbruiks*.csv"`. The python script creates the needed files for the generic import script.
  - Follow the steps in the overall how-to

  [Mijn Fluvius](https://mijn.fluvius.be/) also offers an English version of the site alongside the Dutch one.
  Not only is the site translated, but the exported files are, too.
  For example, `Verbruiks*.csv` becomes `Consumption_*.csv`; field names in the header are in English, and values are translated (e.g., `Afname Nacht` becomes `Offtake Night,` etc.).
  The script `FluviusDataPrepareEN.py` has been adapted to process these English files.

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