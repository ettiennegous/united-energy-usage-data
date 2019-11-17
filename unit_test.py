import pytest
import unittest
from requests import Session
from unitedenergy.unitedenergy import UnitedEnergy
from unitedenergy import PeriodOffset
from unitedenergy import ReportPeriod
from unitedenergy import UnitedEnergyError
from urllib.parse import urlparse
from unittest.mock import patch
from mockresponse import MockResponse

def mocked_negative_post_requests(*args, **keywargs):

    if "login_security_check" in args[0]:
        return MockResponse("login_fail.html", 200)

    return MockResponse("", 404)
    
def mocked_positive_get_requests(*args1, **blah1):

    if "electricityView/isElectricityDataUpdated" in args1[0]:
        return MockResponse("latest_data.json", 200)
    elif "electricityView/latestData" in args1[0]:
        return MockResponse("latest_data.json", 200)
    elif "period/day/0" in args1[0]:
        return MockResponse("current_day.json", 200)
    elif "period/month/0" in args1[0]:
        return MockResponse("current_month.json", 200)
    elif "period/month/1" in args1[0]:
        return MockResponse("prior_month.json", 200)
    elif "period/month/2" in args1[0]:
        return MockResponse("beforelast_month.json", 200)
    elif "period/year/0" in args1[0]:
        return MockResponse("current_year.json", 200)
    return MockResponse("", 404)

def mocked_positive_post_requests(*args, **keywargs):

    if "login_security_check" in args[0]:
        return MockResponse("login_pass.html", 200)

    return MockResponse("", 404)


class TestUnitedFixtureData(unittest.TestCase):
    """Test the United Energy API logic."""

    @patch.object(Session, "post",  side_effect=mocked_positive_post_requests)
    def test_login_pass(self, mock_post):
        ue = UnitedEnergy("test_un", "test_pwd", True)
        assert ue.password is "test_pwd"
        assert ue.username is "test_un"

    @patch.object(Session, "post",  side_effect=mocked_negative_post_requests)
    def test_login_fail(self, mock_post):
        with pytest.raises(UnitedEnergyError):
            ue = UnitedEnergy("test_un", "test_pwd", True)
            assert ue.password is "test_pwd"
            assert ue.username is "test_un"

    @patch.object(Session, "post",  side_effect=mocked_positive_post_requests)
    @patch.object(Session, "get",  side_effect=mocked_positive_get_requests)
    def test_get_meters(self, mock_post, mock_get):
        ue = UnitedEnergy("test_un", "test_pwd", True)
        results = ue.get_meters()
        assert len(results)  == 1
        assert results[0] == "1234567"

    @patch.object(Session, "post",  side_effect=mocked_positive_post_requests)
    @patch.object(Session, "get",  side_effect=mocked_positive_get_requests)
    def test_fetch_recent_usage(self, mock_post, mock_get):
        ue = UnitedEnergy("test_un", "test_pwd", True)
        results = ue.fetch_recent_usage_data(ReportPeriod.day, PeriodOffset.current)
        assert results["latestInterval"]  == "2019-11-11:42"

    @patch.object(Session, "post",  side_effect=mocked_positive_post_requests)
    @patch.object(Session, "get",  side_effect=mocked_positive_get_requests)
    def test_fetch_recent_reformat_usage(self, mock_post, mock_get):
        ue = UnitedEnergy("test_un", "test_pwd", True)
        results = ue.fetch_recent_usage_data_and_reformat(ReportPeriod.day, PeriodOffset.current)
        assert len(results)  == 24

    @patch.object(Session, "post",  side_effect=mocked_positive_post_requests)
    @patch.object(Session, "get",  side_effect=mocked_positive_get_requests)
    def test_fetch_last_reading(self, mock_post, mock_get):
        ue = UnitedEnergy("test_un", "test_pwd", True)
        results = ue.fetch_last_reading(ReportPeriod.day, PeriodOffset.current)
        assert results["price"]  == 0.1543473
        assert results["timestamp"]  == "2019-11-11 20:00"
        assert results["total"]  == 0.951

    @patch.object(Session, "post",  side_effect=mocked_positive_post_requests)
    @patch.object(Session, "get",  side_effect=mocked_positive_get_requests)
    def test_fetch_cumilitive_reading_day(self, mock_post, mock_get):
        ue = UnitedEnergy("test_un", "test_pwd", True)
        results = ue.fetch_cumilitive_reading(ReportPeriod.day, PeriodOffset.current)
        assert results["price"]  == 1.6528631999999999
        assert results["timestamp"]  == "2019-11-11 20:00"
        assert results["total"]  == 10.183999999999997

    @patch.object(Session, "post",  side_effect=mocked_positive_post_requests)
    @patch.object(Session, "get",  side_effect=mocked_positive_get_requests)
    def test_fetch_cumilitive_reading_month(self, mock_post, mock_get):
        ue = UnitedEnergy("test_un", "test_pwd", True)
        results = ue.fetch_cumilitive_reading(ReportPeriod.month, PeriodOffset.timebeforelast)
        assert results["price"]  == 87.37647719999998
        assert results["timestamp"]  == "2019-9-29"
        assert results["total"]  == 538.364

    @patch.object(Session, "post",  side_effect=mocked_positive_post_requests)
    @patch.object(Session, "get",  side_effect=mocked_positive_get_requests)
    def test_fetch_cumilitive_reading_year(self, mock_post, mock_get):
        ue = UnitedEnergy("test_un", "test_pwd", True)
        results = ue.fetch_cumilitive_reading(ReportPeriod.year, PeriodOffset.current)
        assert results["price"]  == 542.2389441
        assert results["timestamp"]  == "2019-10"
        assert results["total"]  == 3340.967