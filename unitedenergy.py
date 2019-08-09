# Copyright (c) 2019 Ettienne Gous <ettiennegous@hotmail.com>

import requests
import json
import time
from enum import Enum
from datetime import datetime
import collections

class DayToReport(Enum):
    today = 0
    yesterday = 1
    twoDaysAgo = 2

class UnitedEnergy():

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.session()
        self.apiBase = 'https://energyeasy.ue.com.au/'
        self.__login()

    def __login(self):
        payload = { 'login_email' : self.username, 'login_password' : self.password, 'submit': 'Login'}
        login_response = self.session.post(self.apiBase + 'login_security_check', data=payload)
        login_response.raise_for_status()
        if('The credentials entered were not recognised' in login_response.content):
            raise Exception('Invalid Login')

    def __fetch_usage_data(self, daysOffSet):
        usage_response = self.session.get(self.apiBase + '/electricityView/period/day/' + str(daysOffSet) + '?_=1565095533911')
        usage_data_obj = json.loads(usage_response.content)
        return usage_data_obj

    def fetch_and_print_most_recent_usage_data(self, day_to_report):
        response_data = self.__fetch_usage_data(day_to_report)
        last_known_interval = response_data['latestInterval']
        if(self.__request_latest_data_update(last_known_interval)):
            self.__poll_electricity_data_updated(last_known_interval)
            response_data = self.__fetch_usage_data()
        self.__print_usage_data(self.__create_usage_data_array(response_data))

    def __print_usage_data(self, data):
        for date_time in data:
            print('{0} - {1}'.format(date_time, data[date_time]))

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
        print (last_known_interval)
        result = 'false'
        while result != 'true':
            poll_response = self.session.get(self.apiBase + '/electricityView/isElectricityDataUpdated?lastKnownInterval=' + last_known_interval)
            print 'Polling for true status on latest data received'
            result = poll_response.content
            time.sleep(2)
        return result

    def __request_latest_data_update(self, last_known_interval):
        request_url = self.apiBase + '/electricityView/latestData?lastKnownInterval=' + last_known_interval + '&_=1565182358706'
        print request_url
        latest_data_response = self.session.get(request_url)
        response_obj = json.loads(latest_data_response.content)
        should_poll = response_obj['poll'] == 'true'
        return should_poll
