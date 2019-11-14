# # Copyright (c) 2019 Ettienne Gous <ettiennegous@hotmail.com>

import json
#from unitedenergy.enums import ReportPeriod, PeriodOffset
#from unitedenergy.unitedenergy import UnitedEnergy
from unitedenergy import UnitedEnergy
from unitedenergy import PeriodOffset
from unitedenergy import ReportPeriod

with open('config.json') as json_data_file:
    config_settings = json.load(json_data_file)
    ue = UnitedEnergy(config_settings['username'], config_settings['password'], True)
    print(ue.get_meters())
    print(ue.fetch_and_print_most_recent_usage_data(ReportPeriod.day, PeriodOffset.current))
    print(ue.fetch_last_reading(ReportPeriod.day, PeriodOffset.current))
