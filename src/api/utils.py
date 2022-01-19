from datetime import date, datetime
import requests

class Utils:
    def get_time_qualifier(self,from_date):
        today = date.today()
        difference_days = (today - from_date).days
        
        if difference_days <= 0:
            return "day"
        if difference_days <= 7:
            return "week"
        if difference_days <= 31:
            return "month"
        if difference_days <= 365:
            return "year"
        return "all"


class Timeframe:
    def __init__(self, from_date, to_date) -> None:
        self.from_date = from_date
        self.to_date   = to_date
        pass

    def is_in_timeframe(self, submission_date):
        return self.from_date <= submission_date <= self.to_date

class database_handler:
    def __init__(self):
        self.data = {
            'ID': 'reddit-1',
            'text': 'text body'
        }

    def insert(self):
        request = requests.post('/hitec/repository/concepts/store/dataset/', data=self.data)
        return request.status_code
    