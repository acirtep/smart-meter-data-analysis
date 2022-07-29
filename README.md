# smart-meter-data-analysis
This repository contains data analysis tips on smart meter historical data.
It expects to have in the input_data folder a file called historical_electricity.xlsx,
which has the following header:
Datum	Levering normaal	Levering dal	Teruglevering normaal	Teruglevering dal	Meternummer	EAN	Product
If you have a different header feel free to change the method get_raw_data from data_analysis.py.

1. Run `docker-compose up --build`
2. Run `docker exec -it smart_meter_DA_container python /app/src/data_analysis.py`
to generate visuals for your own data

![Example](https://github.com/acirtep/smart-meter-data-analysis/blob/main/visuals/frequency_avg.jpg)


3. ipython is also available with `docker exec -it smart_meter_DA_container ipython`
