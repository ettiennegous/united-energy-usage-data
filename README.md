# United Energy Usage Data

This helper class is to read electricity usage data from [Unit Energy's](https://www.unitedenergy.com.au/) [Energy Easy portal](https://energyeasy.ue.com.au).  
United Energy is an electricity distributor for Melbourne Victoria's south eastern suburbs and the Mornington Peninsula.  
If you live in any of these areas you can use this to read your usage information regardless of your energy retailer.  
  
The helper has been written for my use case but can be extended should you want to.  

## Usage
1. Go [here](https://energyeasy.ue.com.au/) and register yourself
1. Edit the config.json with your username and password
1. Run a test with `python manual_test.py`

## Things to do / Future improvements
1. It only reads from the peak tarrif usage information (Thats my use case I would need to see someone else's data to implement it properly for offpeak and shoulder periods)
1. Add mock json files and write unit tests
1. It can only read usage information for today, yesterday and two days ago
1. Implement local file caching to lower latency for fully hydrated day data sets




