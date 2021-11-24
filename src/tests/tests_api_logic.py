import unittest
import datetime

# https://gideonbrimleaf.github.io/2021/01/26/relative-imports-python.html
import sys 
sys.path.append("..")

from api_test.src.api.utils import Utils

class TestUtils(unittest. TestCase):
    
    def setUp(self) -> None:
        self.utils_instance = Utils()
        self.today = datetime.date.today()

    def test_time_qualifier_days_zero(self):        
        from_date = self.today
        qualifier = self.utils_instance.get_time_qualifier(from_date)
        self.assertEqual(qualifier, "day" , "classification for 0 days difference")

    def test_time_qualifier_days_5(self):        
        from_date = self.today - datetime.timedelta(days=5)
        qualifier = self.utils_instance.get_time_qualifier(from_date)
        self.assertEqual(qualifier, "week" , "classification for 5 days difference")

    def test_time_qualifier_days_7(self):        
        from_date = self.today - datetime.timedelta(days=7)
        qualifier = self.utils_instance.get_time_qualifier(from_date)
        self.assertEqual(qualifier, "week" , "classification for 7 days difference")

    def test_time_qualifier_days_8(self):        
        from_date = self.today - datetime.timedelta(days=8)
        qualifier = self.utils_instance.get_time_qualifier(from_date)
        self.assertEqual(qualifier, "month" , "classification for 8 days difference")

    def test_time_qualifier_days_32(self):        
        from_date = self.today - datetime.timedelta(days=32)
        qualifier = self.utils_instance.get_time_qualifier(from_date)
        self.assertEqual(qualifier, "year" , "classification for 32 days difference")

    def test_time_qualifier_days_366(self):        
        from_date = self.today - datetime.timedelta(days=366)
        qualifier = self.utils_instance.get_time_qualifier(from_date)
        self.assertEqual(qualifier, "all" , "classification for 366 days difference")

    def test_timeframe_accept(self):
        from_date = self.today - datetime.timedelta(days=10)
        test_date = self.today - datetime.timedelta(days=5)
        decision = self.utils_instance.in_timeframe(from_date=from_date,to_date=self.today,submission_date=test_date)
        self.assertEqual(decision, True , "Test date in timeframe")

    def test_timeframe_discard(self):
        from_date = self.today - datetime.timedelta(days=10)
        test_date = self.today - datetime.timedelta(days=15)
        decision = self.utils_instance.in_timeframe(from_date=from_date,to_date=self.today,submission_date=test_date)
        self.assertEqual(decision, False , "Test date out of timeframe")


if __name__ == '__main__':
    unittest.main()