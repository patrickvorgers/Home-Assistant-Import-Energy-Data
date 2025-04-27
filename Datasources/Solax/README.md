# Energy provider: Solax

Solax offers the option to export data from the [Solax Cloud](https://www.solaxcloud.com/) site. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Solar production - High resolution (day interval) - kWh

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`
- OpenPyXL python library `pip install openpyxl`
- XLRD python library `pip install xlrd`


**How-to**
- Export data from the [Solax Cloud](https://www.solaxcloud.com/) site
  - Go to the [Solax Cloud](https://www.solaxcloud.com/) site
  - Login with your account
  - Select 'System&Site'
  - Select your 'Site Name'
  - Select 'Statistics Report'
  - Select 'Daily Report'
  - For each month: Select the month and press export
  - The data for each selected month is now downloaded to your PC as a separate file
- Download the `SolaxDataPrepare.py` file and put it in the same directory as the Solax data
- Execute the python script with as parameter the name of the directory which contains the files with the exported data `python SolaxDataPrepare.py *.xls`. The python script creates the needed file for the generic import script.
- Follow the steps in the overall how-to