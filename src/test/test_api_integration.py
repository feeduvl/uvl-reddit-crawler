from sqlite3 import Timestamp
import unittest
from unittest.mock import MagicMock
import praw
from urllib import request

import sys
sys.path.append("..")
from src.api.request_handler import RequestHandler
from src.test.utils import SubmissionMockFactory

class redditMock:
    def __init__(self) -> None:
        subreddit = MagicMock()
        submissions = self.get_submissions()
        subreddit.top.return_value(submissions)
        self.subreddit = subreddit
        pass

    def subreddit(self, subreddit_name):
        return self.subreddit

    def get_submissions(self):
        submission_factory = SubmissionMockFactory()

        title = 'title 1'
        text = 'this is the text of a valid reddit post with valid length'
        comments = ['comment a with sufficient length','another comment a with sufficient length']
        timestamp = '1642793826' # 2022-01-21
        submission_a = submission_factory.get_submission_mock(title, text, comments, timestamp)

        """
        title = ''
        text = ''
        comments = ['','']
        timestamp = '1643188166' # 2022-01-26
        submission_b = submission_factory.get_submission_mock(title, text, comments, timestamp)

        title = ''
        text = ''
        comments = ['','']
        timestamp = ''
        submission_c = submission_factory.get_submission_mock(title, text, comments, timestamp)
        """
        return [submission_a]



class DBHandlerMock:
    documents = []
    collection_name = ''

    def get_documents(self):
        return self.documents

    def insert(self, collection_name, documents):
        self.documents = documents
        self.collection_name = collection_name




class TestAPI(unittest.TestCase):

    def setUp(self) -> None:
        self.request_content = {
            "subreddits":["ubuntu","libreoffice"],
            "collection_names":["ubuntu_data"],
            "date_from":"22-01-2022",
            "date_to":"28-01-2022",
            "min_length_posts":"20",
            "min_length_comments":"10",
            "blacklist_comments":["help"],
            "blacklist_posts":["meme"],
            "replace_urls" : "true",
            "replace_emojis" : "false"
        }

        self.reddit_mock = redditMock()
        """self.reddit_mock = praw.Reddit(
            client_id="P0eMVNdwpy29g3K2LhCPTw",
            client_secret="9s-TrT5HJASoawBN951QWsUQTck-mg",
            user_agent="script:api_test:v1.0.0 (by u/uvl_reddit_crawler)",
        )"""

        self.database_mock = DBHandlerMock()
        self.logger = MagicMock()

    def test_api_request(self):
        # GIVEN
        request_instance = RequestHandler(self.request_content,self.database_mock,self.reddit_mock,self.logger)

        # WHEN
        request_instance.run()

        # THEN
        crawling_content = self.database_mock.get_documents()
        print(crawling_content)

        pass
        
    def __assert_collections(self):
        pass

    def __assert_collection_names(self):
        pass

    def __assert_date_exclusion(self):
        pass

    def __assert_post_length(self):
        pass

    def __assert_comment_length(self):
        pass

    def __assert_blacklist_comments(self):
        pass

    def __assert_blacklist(self):
        pass

    def __assert_url_filtering(self):
        pass

    def __assert_emoji_filtering(self):
        pass



if __name__ == '__main__':
    unittest.main()



