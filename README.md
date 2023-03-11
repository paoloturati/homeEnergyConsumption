# homeEnergyConsumption

This service is powered by Streamlit and does the following:
- query the Octopus API to extract all the consumption data (previous 10000 points)
- let you select a day
- produce a plot for the consumption for the selected day compared with the overall average

**Execution**

Type the following from Terminal

`streamlit run check_your_consumption.py`

**Environment variables**

The credentials to access the Octopus API must be configured as environment variables, type the following

`export USER_ID_OCTOPUS=xxxxxx`
`export URL_ELECTRICITY_OCTOPUS=xxxxxx`

**Requirements**

Type the following

`pip install -r requirements.txt`