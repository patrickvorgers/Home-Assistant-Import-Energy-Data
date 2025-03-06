# Energy provider: MeterN

MeterN is a lightweight set of PHP/JS files that makes a Home energy metering & monitoring solution (see [MeterN site](https://github.com/jeanmarc77/meterN) for more information).
It offers the option to export the data of each tracked energymeter in a CSV file. This data can be transformed and used to import into Home Assistant.

[![meterN demo](https://filedn.eu/lA1ykXBhnSe0rOKmNzxOM2H/images/mN/mn_ss.png)]

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
- Pandas python library ```pip install pandas```

**How-to**
- Export data from your local MeterN site
- Download the ```MeterNDataPrepare.py``` file and put it in the same directory as the downloaded MeterN data
- Execute the python script with as parameter the name of the file that contains the exported data **and** the output file that needs to be generated. The python script creates the needed files for the generic import script.
    - `python3 MeterNDataPrepare.py 1FV_Totale20??.csv elec_solar_high_resolution.csv`
    - `python3 MeterNDataPrepare.py 7Prelievi20??.csv elec_feed_in_tariff_1_high_resolution.csv`
    - `python3 MeterNDataPrepare.py 8Immissioni20??.csv elec_feed_out_tariff_1_high_resolution.csv`
- Follow the steps in the overall how-to
