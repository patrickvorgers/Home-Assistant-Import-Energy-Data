# Datasource: [DSMR-reader](https://dsmr-reader.readthedocs.io)

DSMR-reader offers the option to export data from the local database.
This data can be transformed and used to import into Home Assistant.

## Before you start

In case you are using the P1 to USB cable that is currently connected to DSMR-reader, you need the "future" sensor ids to import the data to.
To create them:

- Stop [DSMR-reader](https://dsmr-reader.readthedocs.io)
- Connect the USB to Home Assistant
- Add the `DSMR Smart Meter` integration
- Wait till there are some readings
- Shutdown Home Assistant and create a backup

The documentation in this repo states that:

```
Ensure that the Home Assistant target sensor has atleast 7 days of data before importing the prepared data.
This is necessary to ensure that the short-term statistics in Home Assistant are correctly calculated and displayed.
```

## Tooling needed

- Python 3
- Python libraries

```bash
pip install pandas
pip install tzlocal
```

## How-to

- Export data from DSMR-reader
  - Go to the DSMR-reader UI and go to `Configuration`
  - Login
  - Click `CSV export` => `Export hour totals to CSV`
  - Select `Hour totals` and select the preferred date range (select the complete range since the data will be overwritten)
  - Click `Download export`
- Download the `DSMR-readerDataPrepare.py` file and put it in the same directory as the exported CSV file
- Execute the python script with as parameter the name of the file that contains the exported data `python DSMR-readerDataPrepare.py dsmr-data-export-hour.csv`.
- Follow the import steps in the [generic how-to](https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data/tree/main?tab=readme-ov-file#database)

## Tips and notes on importing data

**If you want to test without shutting down DSMR-reader or Home Assistant**

- Create a Home Assistant container, e.g.

```bash
podman run -d \
  --name="hass" \
  -v ~/Podmandata/hass:/config \
  -p 8123:8123 \
  --restart=always \
  -e TZ="Europe/Amsterdam" \
  docker.io/homeassistant/home-assistant:2025.10.1

```

- Shutdown the container and create fake sensors by editing the `Configuration.yaml`

```yaml
template:
  - sensor:
      - name: "Gas Meter Gasverbruik"
        unique_id: "119"
        unit_of_measurement: "m³"
        device_class: "gas"
        state: "1000"
        state_class: "total_increasing"
        icon: "mdi:fire"

      - name: "Electricity Meter Energieverbruik Tarief 1"
        unique_id: "122"
        unit_of_measurement: "kWh"
        device_class: "energy"
        state: "1000"
        state_class: "total_increasing"
        icon: "mdi:flash"

      - name: "Electricity Meter Energieverbruik Tarief 2"
        unique_id: "123"
        unit_of_measurement: "kWh"
        device_class: "energy"
        state: "1000"
        state_class: "total_increasing"
        icon: "mdi:flash"

      - name: "Electricity Meter Energieproductie Tarief 1"
        unique_id: "124"
        unit_of_measurement: "kWh"
        device_class: "energy"
        state: "1000"
        state_class: "total_increasing"
        icon: "mdi:solar-power"

      - name: "Electricity Meter Energieproductie Tarief 2"
        unique_id: "125"
        unit_of_measurement: "kWh"
        device_class: "energy"
        state: "1000"
        state_class: "total_increasing"
        icon: "mdi:solar-power"
```

- Start the container again, and verify the new sensors
- Shutdown and use the database

**When using the SQLite version**

When modifying the `Import Energy data into Home Assistant.sqbpro` file in `DB Browser for SQLite` only change the sensor ids, NOT the sensor names.

- Example below with sensor ids `119`, `122`, `123`, `124` and `125`:

```sql
/*                          name                      sensor_id correction cutoff_new_meter cutoff_invalid_value */
INSERT INTO SENSORS VALUES ('gas',                    119,        1.0,    25.0,            1000.0); /* Change */
INSERT INTO SENSORS VALUES ('elec_feed_in_tariff_1',  122,        1.0,    25.0,            1000.0); /* Change */
INSERT INTO SENSORS VALUES ('elec_feed_in_tariff_2',  123,        1.0,    25.0,            1000.0); /* Change */
INSERT INTO SENSORS VALUES ('elec_feed_out_tariff_1', 124,        1.0,    25.0,            1000.0); /* Change */
INSERT INTO SENSORS VALUES ('elec_feed_out_tariff_2', 125,       1.0,    25.0,            1000.0); /* Change */
/*INSERT INTO SENSORS VALUES ('elec_solar',             352,      1000.0,    25.0,            1000.0); /* Change */
/*INSERT INTO SENSORS VALUES ('elec_battery_feed_in',   450,      1000.0,    25.0,            1000.0); /* Change */
/*INSERT INTO SENSORS VALUES ('elec_battery_feed_out',  451,      1000.0,    25.0,            1000.0); /* Change */
/*INSERT INTO SENSORS VALUES ('water',                  653,      1000.0,    25.0,            1000.0); /* Change */
```

**Modifying readings afterwards**

When you need to modify a reading or readings, [you can do that from the UI](https://www.reddit.com/r/homeassistant/comments/14cts2p/how_can_i_delete_a_single_day_of_the_energy_panel/)!
