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
  - Download the `FluviusDataPrepare.py` file and put it in the same directory as the Enphase data
  - Execute the python script with as parameter the name of the file that contains the exported data `python FluviusDataPrepare.py "Verbruiks*.csv"`. The python script creates the needed files for the generic import script.
  - Follow the steps in the overall how-to

  Mijn Fluvius also allows using an English version of their site, besides the Dutch one. And not only the site changes, but the exports are also translated.
  "Verbruiks*.csv" becomes "Consumption_*.csv". The fields change names (the header is in English) and values (eg, "Afname Nacht" becomes "Offtake Night", and so on)
  The script ```FluviusDataPrepareEN.py``` is adapted for the English files

  The changed ```FluviusDataPrepareEN.py``` script also allows (and expects) an initial value. In many cases, the digital meters don't start counting from zero,
  but from a value based on previous consumption and set by the installer. The easiest way to find that value, if you don't have it written down,
  is to generate the files using a value of "0", and then compare the last few values with the ones in HomeAssist database, "statistics" table,
  for the same sensors. Then edit the ```FluviusDataPrepareEN.py```, and replace the 5th parameter (after the recalculate boolean) with the difference
  between the values read from the meter and those calculated by the data preparation.

  Example - if you have an epoch (first column in exported files) with "1703886300", note down the 2nd column value, and compare with the value in the state column
  of the statistics table, in the row with a start_ts value equal to "1703886300". The difference between those will give you the start value.
