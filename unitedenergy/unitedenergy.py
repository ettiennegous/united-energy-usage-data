# Copyright (c) 2019 Ettienne Gous <ettiennegous@hotmail.com>

import requests
import json
import time
import daytoreport
from datetime import datetime
import collections
from daytoreport import DayToReport

class UnitedEnergy():

    def __init__(self, username, password, debug = False):
        self.username = username
        self.password = password
        self.debug = debug
        self.session = requests.session()
        self.apiBase = 'https://energyeasy.ue.com.au/'
        self.__login()
        
    def __log_msg(self, *msgs):
        if self.debug:
            for msg in msgs:
                print(msg),
            print

    def __login(self):
        payload = { 'login_email' : self.username, 'login_password' : self.password, 'submit': 'Login'}
        login_response = self.session.post(self.apiBase + 'login_security_check', data=payload)
        login_response.raise_for_status()
        if('The credentials entered were not recognised' in login_response.content):
            raise Exception('Invalid Login')

    def __fetch_usage_data(self, daysOffSet):
        usage_data_url = self.apiBase + 'electricityView/period/day/' + str(daysOffSet) + '?_=1565095533911'
        self.__log_msg('Fetching Usage Data:', usage_data_url)
        usage_response = self.session.get(usage_data_url)
        usage_data_obj = json.loads(usage_response.content)
        return usage_data_obj

    def get_meters(self):
        meters_array = []
        response_data = self.__fetch_usage_data(DayToReport.today)
        for tarrif_type in self.get_tarrif_types():
            for reading in response_data['selectedPeriod']['consumptionData'][tarrif_type]:
                for kvp in reading['meters'].items():
                    if kvp[0] not in meters_array:
                        meters_array.append(kvp[0])
        return meters_array


    def get_tarrif_types(self):
        return ['peak', 'offpeak', 'shoulder', 'generation']

    def get_report_types(self):
        return ['consumptionData', 'costData']

    def fetch_and_print_most_recent_usage_data(self, day_to_report):
        response_data = self.fetch_recent_usage_data(day_to_report)
        self.__print_usage_data(response_data)

    def fetch_recent_usage_data(self, day_to_report):
        response_data = self.__fetch_usage_data(day_to_report)
        last_known_interval = response_data['latestInterval']
        self.__log_msg('Last known update was: ', last_known_interval)
        if(self.__request_latest_data_update(last_known_interval)):
            self.__poll_electricity_data_updated(last_known_interval)
            response_data = self.__fetch_usage_data(day_to_report)
        return self.__create_usage_data_array(response_data)

    def fetch_last_reading(self, day_to_report):
        data_to_filter = self.fetch_recent_usage_data(day_to_report)
        filtered_results = self.__filter_zero_kwh(data_to_filter)
        return list(filtered_results.items())[-1]

    def __filter_zero_kwh(self, data_to_filter):
        return dict(filter(lambda elem: elem[1] != 0, data_to_filter.items()))

    def __print_usage_data(self, data):
        for date_time in data:
            self.__log_msg('{0} - {1}'.format(date_time, data[date_time]))

    def __create_usage_data_array(self, api_data):
        response_data = collections.OrderedDict()
        hour = 0
        date = datetime.strptime(api_data['selectedPeriod']['subtitle'], '%A %d %B %Y')
        for usageByTheHour in api_data['selectedPeriod']['consumptionData']['peak']:
            dateTime = '{0}-{1}-{2} {3:02d}:00'.format(date.year, date.month, date.day, hour)
            response_data[dateTime] = usageByTheHour['total']
            hour += 1
        return response_data

    def __poll_electricity_data_updated(self, last_known_interval):
        self.__log_msg('Last known interval was:', last_known_interval)
        result = 'false'
        request_url = self.apiBase + 'electricityView/isElectricityDataUpdated?lastKnownInterval=' + last_known_interval
        while result != 'true':
            poll_response = self.session.get(request_url)
            self.__log_msg('Polling for true status on latest data received: ', request_url)
            result = poll_response.content
            time.sleep(2)
        return result

    def __request_latest_data_update(self, last_known_interval):
        request_url = self.apiBase + 'electricityView/latestData?lastKnownInterval=' + last_known_interval + '&_=1565182358706'
        self.__log_msg('Request latest data update: ', request_url)
        latest_data_response = self.session.get(request_url)
        response_obj = json.loads(latest_data_response.content)
        should_poll = response_obj['poll'] == 'true'
        return should_poll
