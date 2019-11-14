import pytest
import unittest
import json
import os
import requests
from requests import Session
import re
from unitedenergy import UnitedEnergy
from unitedenergy import PeriodOffset
from unitedenergy import ReportPeriod
from unitedenergy import UnitedEnergyError
from urllib.parse import urlparse
from unittest.mock import patch

class MockResponse:
    """Class to represent a mocked response."""

    def __init__(self, fixture_to_load, status_code):
        """Initialize the mock response class."""
        self.content = self.load_fixture(fixture_to_load)
        self.status_code = status_code

    def raise_for_status(self):
        """Raise an HTTPError if status is not 200."""
        if self.status_code != 200:
            raise requests.HTTPError(self.status_code)

    def load_fixture(self, filename):
        """Load a fixture."""
        path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
        with open(path, "rb") as fptr:
            return fptr.read()

class TestUnitedFixtureData(unittest.TestCase):
    """Test the United Energy API logic."""

    @patch.object(Session, "post",  return_value=MockResponse("login_pass.html", 200))
    def test_login_pass(self, mock_get):
        ue = UnitedEnergy("test_un", "test_pwd", True)
        assert ue.password is "test_pwd"
        assert ue.username is "test_un"

    @patch.object(Session, "post",  return_value=MockResponse("login_fail.html", 200))
    def test_login_fail(self, mock_get):
        with pytest.raises(UnitedEnergyError):
            ue = UnitedEnergy("test_un", "test_pwd", True)
            assert ue.password is "test_pwd"
            assert ue.username is "test_un"