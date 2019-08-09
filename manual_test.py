# Copyright (c) 2019 Ettienne Gous <ettiennegous@hotmail.com>

import json
from unitedenergy import DayToReport
from unitedenergy import UnitedEnergy

with open('config.json') as json_data_file:
    config_settings = json.load(json_data_file)
    ue = UnitedEnergy(config_settings['username'], config_settings['password'])
    ue.fetch_and_print_most_recent_usage_data(DayToReport.today)

