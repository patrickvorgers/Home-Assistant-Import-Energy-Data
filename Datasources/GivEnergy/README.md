# Energy provider: GivEnergy

GivEnergy offers the option to download historical energy data from the [GivEnergy Cloud](https://givenergy.cloud/) portal through an API. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (hour interval) - kWh
- Electricity production - Tariff 1 - High resolution (hour interval) - kWh
- Battery charge - Tariff 1 - High resolution (hour interval) - kWh
- Battery discharge - Tariff 1 - High resolution (hour interval) - kWh
- Solar production - High resolution (hour interval) - kWh

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`
- Requests python library `pip install requests`
- Tzlocal python library `pip install tzlocal`

**How-to**

1. **Prerequisites (Serial Number + API Token)**

   - **Inverter Serial Number**<br>
     The serial number is that of the inverter. The serial number is 10 characters long (often starting with `FD`).

   - **Create an API Token (GivEnergy Cloud portal)**
     - Log in to the GivEnergy Cloud dashboard.
     - Go to **Account Settings**.
     - Select **Manage Account Security**.
     - Scroll to **Manage API Tokens** and select **Generate New Token**.
     - Provide:
        - **Name**: any descriptive name (e.g. `HA Import`) 
        - **Expiry date**: for one-off exports it is recommended to set a short expiry (e.g. **1 day** or **1 week**) so the token automatically expires after you have downloaded the data.
        - **Scope**: select **api: Full Control** (simple option) or pick the read scopes that match what you need.
     <br><br>
     > Notes:
     > - The same API token can typically be used across multiple inverters on the same account.
     > - If a token expires (or is revoked), simply generate a new one and re-run the download.

2. **Download data for an interval (GrabGivEnergyData.py)**
   - Download the `GrabGivEnergyData.py` script.
   - Create a file which contains the API token which was just created (example: `api_token.txt`).
   - Run the script to fetch the data for a specific period. Use `--help` (or `-h`) to see the supported parameters:
     - `python GrabGivEnergyData.py --help`
   - Example (adjust parameters to the desired output):
     - `python GrabGivEnergyData.py --serial FDxxxxxxxx --api-token-file api_token.txt --start 2025-01-01 --end 2025-01-31`

3. **Prepare the downloaded data for Home Assistant import**
   - Download the `GivEnergyDataPrepare.py` and the `DataPrepareEngine.py` (Datasources directory) files and put them in the same directory as the downloaded GivEnergy data.
   - Execute the python script with as parameter the the name of the file(s) that contain the exported data `python GivEnergyDataPrepare.py *.json`. The python script creates the needed file for the generic import script.
   - Follow the steps in the overall how-to
