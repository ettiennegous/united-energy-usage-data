import os
import requests

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