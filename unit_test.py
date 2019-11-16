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
    elif "period" in args1[0]:
        return MockResponse("today_hourly.json", 200)

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