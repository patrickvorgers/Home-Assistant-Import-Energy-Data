# Energy provider: SolarEdge

SolarEdge offers the option to export data from the [Solar Edge](https://www.solaredge.com/) website through an API. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Solar production - High resolution (hour interval) - Wh

**Tooling needed**
- Python 3
- Pandas python library ```pip install pandas```


**How-to**
- Export data using the <i>Site Energy API</i> (see online [API documentation](https://knowledge-center.solaredge.com/sites/kc/files/se_monitoring_api.pdf#page=14)). Use multiple exports in case the needed period exceeds the API limitation (one month/one year - depending on resolution)
- Download the ```SolarEdgeDataPrepare.py``` file and put it in the same directory as the SolarEdge json data
- Execute the python script with as parameter the name of the directory which contains the files with the exported data ```python SolarEdgeDataPrepare.py *.json```. The python script creates the needed file for the generic import script.
- Follow the steps in the overall how-to