import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import requests


def format_date(date_string, wanted_feature):
    """
    This method, given an input date string and a wanted feature,
    returns either year, month, day, hour and minute.

    For example, given this input "2023-04-16T00:30:00+01:00",
    it will return the year as 2023, the month as 04, the day as 16,
    the hour as 00 and the minute as 30.
    """

    if "T" not in date_string:
        # date is in the wrong format
        return np.nan

    if wanted_feature in ["year", "month", "day"]:
        date_part = date_string.split("T")[0]
        try:
            year = int(date_part.split("-")[0])
            month = int(date_part.split("-")[1])
            day = int(date_part.split("-")[2])
        except:
            # date part has the wrong format
            year = np.nan
            month = np.nan
            day = np.nan
        if wanted_feature == "year":
            return year
        elif wanted_feature == "month":
            return month
        else:
            return day
    elif wanted_feature in ["hour", "minute"]:
        hour_part = date_string.split("T")[1]
        try:
            hour = int(hour_part.split(":")[0])
            minute = int(hour_part.split(":")[1])
        except:
            # hour part has the wrong format
            hour = np.nan
            minute = np.nan
        if wanted_feature == "hour":
            return hour
        else:
            return minute
    else:
        # wanted feature not available
        return np.nan

class Utilities:
    def __init__(self, url_string, user_id):
        self.url_string = url_string
        self.user_id = user_id
        self.data_integrity = True

    def retrieve_readings(self):
        """
        This method executes the HTTP get request
        to the Octopus API.
        """

        params = {"page_size": 10000}
        self.response_electricity = requests.get(
            self.url_string,
            auth=(self.user_id, ""),
            params=params,
        )

    def parse_data(self):
        """
        This method parses the data retrieved in the HTTP
        request.
        """

        response_str = self.response_electricity.text
        response_str = response_str.replace("null", "None")
        response_dict = eval(response_str)

        self.results_df = pd.DataFrame(response_dict["results"])

    def extract_time_metrics(self):
        """
        This method computes the time metrics of the
        retrieved data.
        """

        self.results_df["year_start"] = self.results_df["interval_start"].apply(format_date, args=("year",))
        self.results_df["month_start"] = self.results_df["interval_start"].apply(format_date, args=("month",))
        self.results_df["day_start"] = self.results_df["interval_start"].apply(format_date, args=("day",))
        self.results_df["hour_start"] = self.results_df["interval_start"].apply(format_date, args=("hour",))
        self.results_df["minute_start"] = self.results_df["interval_start"].apply(format_date, args=("minute",))
        self.results_df["year_end"] = self.results_df["interval_end"].apply(format_date, args=("year",))
        self.results_df["month_end"] = self.results_df["interval_end"].apply(format_date, args=("month",))
        self.results_df["day_end"] = self.results_df["interval_end"].apply(format_date, args=("day",))
        self.results_df["hour_end"] = self.results_df["interval_end"].apply(format_date, args=("hour",))
        self.results_df["minute_end"] = self.results_df["interval_end"].apply(format_date, args=("minute",))

    def check_daily_consumption(self, day_string):

        self.day_string = day_string
        # extract day, month, year from input
        day = int(day_string.split("-")[2])
        month = int(day_string.split("-")[1])
        year = int(day_string.split("-")[0])

        # select only relevant data
        self.daily_results_df = self.results_df[
            (
                (self.results_df["day_end"] == day)
                & (self.results_df["month_end"] == month)
                & (self.results_df["year_end"] == year)
            )
        ].copy()

        if self.daily_results_df.shape[0] < 48:
            self.data_integrity = False

    def plot_results(self):

        # compute average consumption in a day
        avg_consumption = self.results_df.groupby(["hour_end", "minute_end"])[
            "consumption"
        ].mean()

        daily_consumption = self.daily_results_df.groupby(["hour_end", "minute_end"])[
            "consumption"
        ].mean()
        daily_diff = round((daily_consumption.sum() - avg_consumption.sum()), 2)
        title = (
            "Consumption on "
            + self.day_string
            + " - Difference: "
            + str(daily_diff)
            + " kW"
        )

        self.fig = plt.figure(figsize=(20, 6))

        avg_consumption.plot(label="average")
        daily_consumption.plot(label="daily")
        plt.grid()
        plt.legend()
        plt.title(title)
        plt.show()


if __name__ == "__main__":

    # read credentials as environment variables
    url_string_electricity = os.getenv("URL_ELECTRICITY_OCTOPUS")
    user_id = os.getenv("USER_ID_OCTOPUS")

    # initialise object
    session = Utilities(url_string=url_string_electricity, user_id=user_id)

    session.retrieve_readings()
    session.parse_data()
    session.extract_time_metrics()
    # for testing purposes only
    session.check_daily_consumption("2023-04-13")
