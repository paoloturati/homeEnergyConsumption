import pandas as pd
import matplotlib.pyplot as plt
import requests


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

        self.results_df["interval_start"] = pd.to_datetime(
            self.results_df["interval_start"]
        )
        self.results_df["interval_end"] = pd.to_datetime(
            self.results_df["interval_end"]
        )
        self.results_df["year_start"] = self.results_df["interval_start"].dt.year
        self.results_df["month_start"] = self.results_df["interval_start"].dt.month
        self.results_df["day_start"] = self.results_df["interval_start"].dt.day
        self.results_df["hour_start"] = self.results_df["interval_start"].dt.hour
        self.results_df["minute_start"] = self.results_df["interval_start"].dt.minute
        self.results_df["year_end"] = self.results_df["interval_end"].dt.year
        self.results_df["month_end"] = self.results_df["interval_end"].dt.month
        self.results_df["day_end"] = self.results_df["interval_end"].dt.day
        self.results_df["hour_end"] = self.results_df["interval_end"].dt.hour
        self.results_df["minute_end"] = self.results_df["interval_end"].dt.minute

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
