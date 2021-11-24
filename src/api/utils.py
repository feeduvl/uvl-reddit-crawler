from datetime import date, datetime

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

    def in_timeframe(self, submission_date,from_date,to_date):
        return from_date <= submission_date <= to_date
