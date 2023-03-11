import streamlit as st
import os
from Library import utilities

# read credentials as environment variables
url_string_electricity = os.getenv("URL_ELECTRICITY_OCTOPUS")
user_id = os.getenv("USER_ID_OCTOPUS")

# initialise object
session = utilities.Utilities(url_string=url_string_electricity, user_id=user_id)

session.retrieve_readings()
session.parse_data()
session.extract_time_metrics()

st.title("Check your daily Energy Consumption")
st.write("Select a day and see how you compared to your average")

# get day from user
day_string = str(st.date_input("Select day"))

# check daily data
session.check_daily_consumption(day_string)

if session.data_integrity:
    # we have data for the selected day
    session.plot_results()
    st.pyplot(session.fig)
else:
    st.write("Sorry, no data for the day you selected.")
