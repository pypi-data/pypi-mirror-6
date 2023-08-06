import unittest
from libyr import Yr
#from requests.exceptions import HTTPError

class YrTestCase(unittest.TestCase):

    _multiprocess_can_split_ = True

    def setUp(self):
        """Create simple data set with headers."""
        pass

    def tearDown(self):
        """Teardown."""
        pass

    def test_weather_now(self):
    	weather = Yr('Norge/Telemark/Skien/Skien')
        r = weather.now()
        assert r['time']

    def test_assign_wrong_path(self):
        pass

def main():
    unittest.main()

if __name__ == '__main__':
    main()
