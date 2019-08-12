# Copyright (c) 2019 Ettienne Gous <ettiennegous@hotmail.com>

import json
from unitedenergy import UnitedEnergy
from unitedenergy import DayToReport

with open('config.json') as json_data_file:
    config_settings = json.load(json_data_file)
    ue = UnitedEnergy(config_settings['username'], config_settings['password'], True)
    print ue.get_meters()
    print ue.fetch_last_reading(DayToReport.today)

