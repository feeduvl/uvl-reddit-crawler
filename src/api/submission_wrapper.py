

from datetime import datetime
#from utils import Timeframe


class SubmissionWrapper:
    def __init__(self, submission, timeframe) -> None:
        self.valid = True
        self.timeframe = timeframe
        self.title = self.__check_title(submission.title)
        self.selftext = self.__check_selftext(submission.selftext)
        self.comments = self.__check_comments(submission.comments.list())

    def __check_title(self, title):
        return title

    def __check_selftext(self, selftext):
        if len(selftext) < 20:
            self.valid = False
        return selftext

    def __check_comments(self,comments):
        checked_comments = []
        for comment in comments:       # pythonic refactoring required
            try:
                if len(comment.body) > 5:  # arbitrary min length (tbd)
                    checked_comments.append(comment)
            except AttributeError:
                continue
        return checked_comments

    def __check_submission(self,submission):
        submission_date = datetime.utcfromtimestamp(int(submission.created_utc)).date()
        if self.timeframe.is_in_timeframe(submission_date) == False:
            self.valid = False
        pass

    def __get_submission_data(self):
        submission_title = self.title
        submission_text = self.selftext
        submission_comments = []
        for comment in self.comments:
            try:
                submission_comments.append(comment.body)
            except AttributeError:
                continue
        return submission_title, submission_text, submission_comments

    def get(self):
        documents = []
        submission_title, submission_text, submission_comments = self.__get_submission_data()
        document = { "title": submission_title, "text": submission_text, "comments" : submission_comments }
        documents.append(document)
        return document

    