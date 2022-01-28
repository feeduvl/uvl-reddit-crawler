import unittest
from unittest.mock import MagicMock

class SubmissionMockFactory():

    def __init__(self) -> None:
        pass

    def get_submission_mock(self,title,text,comments=[],timestamp=''):
        submission_mock = MagicMock()
        submission_mock.title = title
        submission_mock.selftext = text
        submission_mock.created_utc = timestamp

        comments_mock_return_list = []
        for comment in comments:
            comment_mock = MagicMock()
            comment_mock.body = comment
            comments_mock_return_list.append(comment_mock)

        comments_mock = MagicMock()
        comments_mock.list.return_value = comments_mock_return_list

        submission_mock.comments = comments_mock
        return submission_mock