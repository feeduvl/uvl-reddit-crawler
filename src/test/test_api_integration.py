from sqlite3 import Timestamp
import unittest
from unittest.mock import MagicMock
import praw
from urllib import request

import sys
sys.path.append("..")
from src.api.request_handler import RequestHandler
from src.test.utils import RedditMockFactory


class DBHandlerMock:
    def __init__(self) -> None:
        self.documents = []
        self.collection_names = []
        pass

    def get_documents(self):
        return self.documents

    def insert(self, collection_name, documents):
        self.documents.append(documents)
        self.collection_names.append(collection_name)


class TestAPI(unittest.TestCase):

    def setUp(self) -> None:
        self.request_content = {
            "subreddits":["ubuntu","libreoffice"],
            "collection_names":["ubuntu_data","libredata"],
            "date_from":"22-01-2022",
            "date_to":"28-01-2022",
            "min_length_posts":"20",
            "min_length_comments":"8",
            "blacklist_comments":["help"],
            "blacklist_posts":["meme"],
            "replace_urls" : "true",
            "replace_emojis" : "false"
        }

        self.database_mock = DBHandlerMock()
        self.logger = MagicMock()
        self.mock_factory = RedditMockFactory()
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()


    def test_request_all_valid(self):
        # GIVEN
        reddit_mock, crawler_result = self.mock_factory.get()
        request_instance = RequestHandler(self.request_content,self.database_mock,reddit_mock,self.logger)

        # WHEN
        request_instance.run()

        # THEN
        crawling_content = self.database_mock.get_documents()[1]

        self.assertEqual(self.request_content.get("collection_names"),self.database_mock.collection_names)
        self.assertEqual(crawling_content[1].get("Text"), crawler_result)
        pass


    def test_request_omit_collection_name(self):
        # GIVEN
        reddit_mock, crawler_result = self.mock_factory.get()
        self.request_content["collection_names"] = ["ubuntu_data"]
        request_instance = RequestHandler(self.request_content,self.database_mock,reddit_mock,self.logger)

        # WHEN
        request_instance.run()

        # THEN
        self.assertEqual(self.request_content.get("collection_names")[0],self.database_mock.collection_names[0])
        self.assertEqual(self.database_mock.collection_names[1],"libreoffice_22-01-2022_28-01-2022")
        pass


if __name__ == '__main__':
    unittest.main()



