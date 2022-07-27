"""This module contains utility classes for the crawler API:

Utils: A class that is responsible to create valid reddit time formats
(day, week, moth, years, all) for a given date.

Timeframe: This class uses instances of datetime.date to calculate
if a date is inside or outside of two dates.

DatabaseHandler: A database access class that write directly to database
of feed.uvl.
"""
from datetime import date
import requests

class Utils:
    """Utility class to convert a date to a reddit timeframe option.
    
    Options: day, week, moth, years, all
    """
    def get_time_qualifier(self,from_date):
        """Getter method for a reddit time option for a given date."""
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
    """Utility class to allow calculation if a date is in a given
    timeframe.
    """
    def __init__(self, from_date, to_date) -> None:
        self.from_date = from_date
        self.to_date   = to_date

    def is_in_timeframe(self, submission_date):
        """Returns if a given date is in the timeframe."""
        return self.from_date <= submission_date <= self.to_date

class DatabaseHandler:
    """Utility database access class for feed.uvl."""
    def insert(self, collection_name, documents, logger):
        """Insert a collection into the database.
        
        The documents are a list of dictionaries that contain the keys Id and
        Text.
        """
        
        response = requests.get(f'https://feed-uvl.ifi.uni-heidelberg.de/hitec/repository/concepts/dataset/name/{collection_name}')
        existing_collection = response.json()
        logger.info(existing_collection)

        if not existing_collection["documents"]:
            logger.info('no existing collection detected')
            # create a new collection on DB
            collection = {
                'Name' : collection_name,
                'Documents' : documents
            }

            request = requests.post('https://feed-uvl.ifi.uni-heidelberg.de/hitec/repository/concepts/store/dataset/', json=collection)
            return request.status_code
        else:
            logger.info('existing collection detected')

            # append the documents to the existing collection
            existing_collection["documents"] += documents
            logger.info(existing_collection)
            request = requests.post('https://feed-uvl.ifi.uni-heidelberg.de/hitec/repository/concepts/store/dataset/', json=existing_collection)
            return request.status_code
        