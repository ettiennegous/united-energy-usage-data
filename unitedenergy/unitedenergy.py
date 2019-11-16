# Copyright (c) 2019 Ettienne Gous <ettiennegous@hotmail.com>
"""Helper class that communicates with the United Energy APIs and website."""
import json
from datetime import datetime
import time
import logging
import requests
from .reportperiod import ReportPeriod
from .periodoffset import PeriodOffset
from .unitedenergyerror import UnitedEnergyError

_LOGGER = logging.getLogger(__name__)

class UnitedEnergy:
    """United Energy Website and API abstraction."""

    def __init__(self, username, password, debug=False):
        self.username = username
        self.password = password
        self.debug = debug
        self.session = requests.session()
        self.apibase = "https://energyeasy.ue.com.au/"
        self.__login()

    def __log_msg(self, *msgs):
        if self.debug:
            for msg in msgs:
                _LOGGER.debug(msg)

    def __login(self):
        payload = {
            "login_email": self.username,
            "login_password": self.password,
            "submit": "Login",
        }
        login_response = self.session.post(
            f"{self.apibase}login_security_check", data=payload
        )

        login_response.raise_for_status()
        if "You are logged in as".encode() not in login_response.content:
            raise UnitedEnergyError("Couldnt validate the login")
        if (
            "The credentials entered were not recognised".encode()
            in login_response.content
        ):
            raise UnitedEnergyError("Invalid Login")

    def __fetch_usage_data(
        self, reportperiod: ReportPeriod, periodoffset: PeriodOffset
    ):
    
        usage_data_url = f"{self.apibase}electricityView/period/{str(reportperiod.value)}/{str(periodoffset.value)}?_={str(datetime.timestamp(datetime.now()))}"
        self.__log_msg("Fetching Usage Data:", usage_data_url)
        usage_response = self.session.get(usage_data_url)
        usage_data_obj = json.loads(usage_response.content)
        return usage_data_obj

    def get_meters(self):
        """Fetches the meters setup within your account."""
        meters_array = []
        response_data = self.fetch_recent_usage_data(
            ReportPeriod.year, PeriodOffset.current
        )
        for tarrif_type in self.get_tarrif_types():
            for reading in response_data["selectedPeriod"]["consumptionData"][
                tarrif_type
            ]:
                for kvp in reading["meters"].items():
                    if kvp[0] not in meters_array:
                        meters_array.append(kvp[0])
                        self.__log_msg("Found a meter!: {0}".format(kvp[0]))
        return meters_array

    def get_tarrif_types(self):
        """Fetches different tarrif types that could be reported on."""
        return ["peak", "offpeak", "shoulder", "generation"]

    def get_report_types(self):
        """Fetches report types."""
        return ["consumptionData", "costData"]

    def fetch_and_print_most_recent_usage_data(
        self, reportperiod: ReportPeriod, periodoffset: PeriodOffset
    ):
        """Fetches usage data and prints it out."""
        response_data = self.fetch_recent_usage_data(reportperiod, periodoffset)
        self.__print_usage_data(response_data)

    def fetch_recent_usage_data(
        self, reportperiod: ReportPeriod, periodoffset: PeriodOffset
    ):
        """Fetches recent usage for a timespan and offset."""
        response_data = self.__fetch_usage_data(reportperiod, periodoffset)
        last_known_interval = response_data["latestInterval"]
        self.__log_msg("Last known update was: ", last_known_interval)
        if self.__request_latest_data_update(last_known_interval):
            self.__poll_electricity_data_updated(last_known_interval)
            response_data = self.__fetch_usage_data(reportperiod, periodoffset)
        return response_data

    def fetch_recent_usage_data_and_reformat(
        self, reportperiod: ReportPeriod, periodoffset: PeriodOffset
    ):
        """Fetches recent usage for a timespan and offset and creates an array of objects that can be filtered."""
        return self.__create_usage_data_array(
            self.fetch_recent_usage_data(reportperiod, periodoffset), reportperiod
        )

    def fetch_last_reading(
        self, reportperiod: ReportPeriod, periodoffset: PeriodOffset
    ):
        """Fetches recent usage but only returns the last reading from the collection."""
        data_to_filter = self.fetch_recent_usage_data_and_reformat(
            reportperiod, periodoffset
        )
        filtered_results = self.__filter_zero_kwh(data_to_filter)
        return filtered_results[-1]

    def fetch_cumilitive_reading(
        self, reportperiod: ReportPeriod, periodoffset: PeriodOffset
    ):
        """Fetches all the usage for a timespan and sums the results for a rolling cumulative."""
        usage_data = self.fetch_recent_usage_data(reportperiod, periodoffset)
        collection_date = self.__extract_collection_timestamp(usage_data, reportperiod)
        response_data = {"total": 0, "price": 0, "timestamp": ""}
        for index, value in enumerate(
            usage_data["selectedPeriod"]["consumptionData"]["peak"]
        ):
            if (
                value["total"] == 0
            ):  # This may not work if you actually use no power at all for an interval, most houses will have continual load.
                break

            response_data["total"] += value["total"]
            response_data["timestamp"] = self.__derive_timestamp_from_array_position(
                reportperiod, collection_date, index
            )
            response_data["price"] += usage_data["selectedPeriod"]["costData"]["peak"][
                index
            ]["total"]
            self.__log_msg(
                "New total {0} {1}".format(response_data["total"], value["total"])
            )

        return response_data

    def __filter_zero_kwh(self, data_to_filter):
        """Filters all reporting data to remove records that repo 0 and are likely in the future or awaiting for the data to become available."""
        return list(filter(lambda elem: elem["total"] != 0, data_to_filter))

    def __print_usage_data(self, data):
        """Dump all the usage data to console for debugging."""
        for date_time in data:
            self.__log_msg("{0} - {1}".format(date_time, data[date_time]))

    def __extract_collection_timestamp(self, data, reportperiod: ReportPeriod):
        date = {}
        subtitle = data["selectedPeriod"]["subtitle"]
        if reportperiod == ReportPeriod.day:
            date = datetime.strptime(subtitle, "%A %d %B %Y")
        elif reportperiod == ReportPeriod.month:
            date = datetime.strptime(subtitle, "%B %Y")
        elif reportperiod == ReportPeriod.year:
            date = datetime.strptime(subtitle, "%Y")
        else:
            raise Exception("Invalid Report Period")
        return date

    def __derive_timestamp_from_array_position(
        self, reportperiod: ReportPeriod, collection_date, array_position
    ):
        timestamp = ""
        if reportperiod == ReportPeriod.day:
            timestamp = "{0}-{1}-{2} {3:02d}:00".format(
                collection_date.year,
                collection_date.month,
                collection_date.day,
                array_position,
            )
        elif reportperiod == ReportPeriod.month:
            timestamp = "{0}-{1}-{2}".format(
                collection_date.year, collection_date.month, array_position
            )
        elif reportperiod == ReportPeriod.year:
            timestamp = "{0}-{1}".format(collection_date.year, array_position)
        else:
            raise Exception("Invalid Report Period")
        return timestamp

    def __create_usage_data_array(self, api_data, reportperiod: ReportPeriod):
        response_array = []
        collection_date = self.__extract_collection_timestamp(api_data, reportperiod)

        for index, value in enumerate(
            api_data["selectedPeriod"]["consumptionData"]["peak"]
        ):
            timestamp = self.__derive_timestamp_from_array_position(
                reportperiod, collection_date, index
            )
            response_data = {
                "timestamp": timestamp,
                "total": value["total"],
                "price": api_data["selectedPeriod"]["costData"]["peak"][index]["total"],
            }
            response_array.append(response_data)

        return response_array

    def __poll_electricity_data_updated(self, last_known_interval):
        self.__log_msg("Last known interval was:", last_known_interval)
        result = "false"
        request_url = f"{self.apibase}electricityView/isElectricityDataUpdated?lastKnownInterval={last_known_interval}"

        while result != "true":
            poll_response = self.session.get(request_url)
            self.__log_msg(
                "Polling for true status on latest data received: ", request_url
            )
            result = poll_response.content
            time.sleep(2)
        return result

    def __request_latest_data_update(self, last_known_interval):
        request_url = f"{self.apibase}electricityView/latestData?lastKnownInterval={last_known_interval}&_={str(datetime.timestamp(datetime.now()))}"
        self.__log_msg("Request latest data update: ", request_url)
        latest_data_response = self.session.get(request_url)
        response_obj = json.loads(latest_data_response.content)
        if "poll" in response_obj:
            return response_obj["poll"]
        else:
            raise UnitedEnergyError("Did not receive data to determine if polling is required")


