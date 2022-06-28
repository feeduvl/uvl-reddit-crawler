"""This module contains integration tests that mainly use ReqestHandler as
class under test.

To test this class independently of the praw reddit API, mock classes are
used. The respective mock classes can be found in test/utils.

The unit tests use different variations of HTTP request parameters to assert
if the preprocessing options are routed as intended and functional.
"""
import unittest
import os
from unittest.mock import MagicMock

import sys
sys.path.append("..")
from src.api.request_handler import RequestHandler
from src.test.utils import RedditMockFactory, DBHandlerMock

class TestAPI(unittest.TestCase):
    """This class contains integration tests for the reddit crawler API.
    The class under test is RequestHandler.

    The tests use a praw reddit API mock to ensure independence of the test.
    A database mock is used to capture the crawling results."""
    def setUp(self) -> None:
        self.request_content = {
            "subreddits":["ubuntu"],
            "dataset_name":"ubuntu_data",
            "date_from":"24-01-2022",
            "date_to":"28-01-2022",
            "post_selection": "top",
            "new_limit":"0",
            "min_length_posts":"20",
            "min_length_comments":"10",
            "comment_depth" : "1",
            "blacklist_comments":[],
            "blacklist_posts":[],
            "replace_urls" : "false",
            "replace_emojis" : "false"
        }

        self.database_mock = DBHandlerMock()
        self.logger = MagicMock()
        self.mock_factory = RedditMockFactory()
        self.sep = os.linesep
        return super().setUp()

    def test_request_all_valid(self):
        """Tests request handler without special handling."""
        # GIVEN
        reddit_mock = self.mock_factory.get()
        request_instance = RequestHandler(self.request_content,self.database_mock,reddit_mock,self.logger)

        # WHEN
        request_instance.run()

        # THEN
        crawling_content = self.database_mock.get_documents()[0]

        self.assertEqual(self.request_content.get("collection_names"),self.database_mock.collection_names)
        self.assertEqual(len(crawling_content),2)

        expected_text = self.mock_factory.title + self.sep + self.mock_factory.submission_text + self.sep
        expected_text += self.sep.join(self.mock_factory.comments_all_valid)
        self.assertEqual(self.database_mock.get_text(),expected_text)

    def test_request_omit_collection_name(self):
        # GIVEN: 2 subreddits to crawl
        reddit_mock = self.mock_factory.get()
        self.request_content["subreddits"].append("libreoffice")
        request_instance = RequestHandler(self.request_content,self.database_mock,reddit_mock,self.logger)

        # WHEN
        request_instance.run()

        # THEN: Expect 1 specified collection name, 1 generated collection name
        self.assertEqual(self.request_content.get("collection_names")[0],self.database_mock.collection_names[0])
        self.assertEqual(self.database_mock.collection_names[1],"libreoffice_24-01-2022_28-01-2022")

    def test_request_invalid_date(self):
        # GIVEN: 1 control submission with valid date, 1 test submission with invalid date
        reddit_mock = self.mock_factory.get(date_invalid=True)
        request_instance = RequestHandler(self.request_content,self.database_mock,reddit_mock,self.logger)

        # WHEN
        request_instance.run()

        # THEN: Expect to only get the control submission
        self.assertEqual(len(self.database_mock.get_documents()),1)

    def test_request_invalid_text_len(self):
        # GIVEN: 1 control submission, 1 test submission with short title
        reddit_mock = self.mock_factory.get(short_submission=True)
        request_instance = RequestHandler(self.request_content,self.database_mock,reddit_mock,self.logger)

        # WHEN
        request_instance.run()

        # THEN: Expect to only get the control submission
        self.assertEqual(len(self.database_mock.get_documents()),1)

    def test_request_short_comment(self):
        # GIVEN: 1 control submission, 1 test submission with short comment
        reddit_mock = self.mock_factory.get(short_comment=True)
        request_instance = RequestHandler(self.request_content,self.database_mock,reddit_mock,self.logger)

        # WHEN
        request_instance.run()

        # THEN: Expect to not get short comment text
        self.assertFalse(self.mock_factory.text_short in self.database_mock.get_documents()[0][1].get('Text'))

    def test_request_blacklist_post(self):
        # GIVEN: 1 control submission, 1 test submission with short title
        reddit_mock = self.mock_factory.get(blacklist_in_post=True)
        self.request_content["blacklist_posts"] = [self.mock_factory.blacklist_word]
        request_instance = RequestHandler(self.request_content,self.database_mock,reddit_mock,self.logger)

        # WHEN
        request_instance.run()

        # THEN: Expect to only get the control submission
        self.assertEqual(len(self.database_mock.get_documents()),1)

    def test_request_blacklist_comment(self):
        # GIVEN: 1 control submission, 1 test submission with short title
        reddit_mock = self.mock_factory.get(blacklist_in_comment=True)
        self.request_content["blacklist_posts"] = [self.mock_factory.blacklist_word]
        request_instance = RequestHandler(self.request_content,self.database_mock,reddit_mock,self.logger)

        # WHEN
        request_instance.run()

        # THEN: Expect to only get the control submission
        self.assertFalse(self.mock_factory.blacklist_word in self.database_mock.get_documents()[0][1].get('Text'))

    def test_request_remove_url_text(self):
        # GIVEN: 1 control submission, 1 submission that contains an url in text
        reddit_mock = self.mock_factory.get(contains_url=True)
        self.request_content["replace_urls"] = "true"
        request_instance = RequestHandler(self.request_content,self.database_mock,reddit_mock,self.logger)

        # WHEN
        request_instance.run()

        # THEN: Expect to not find url in text
        self.assertFalse(self.mock_factory.url_string in self.database_mock.get_documents()[0][1].get('Text'))
        
    def test_request_remove_emoji_text(self):
        # GIVEN: 1 control submission, 1 submission that contains an url in text
        reddit_mock = self.mock_factory.get(contains_emoji=True)
        self.request_content["replace_emojis"] = "true"
        request_instance = RequestHandler(self.request_content,self.database_mock,reddit_mock,self.logger)

        # WHEN
        request_instance.run()

        # THEN: Expect to not find url in text
        self.assertFalse(self.mock_factory.emoji_string in self.database_mock.get_documents()[0][1].get('Text'))

    def test_request_comment_depth_1(self):
        # GIVEN: 1 control submission and one submission with comment tree
        reddit_mock = self.mock_factory.get(comment_tree=True)
        request_instance = RequestHandler(self.request_content,self.database_mock,reddit_mock,self.logger)

        # WHEN
        request_instance.run()

        # THEN: Expect to not "level 3" in text
        self.assertFalse("level 2" in self.database_mock.get_text())

    def test_request_comment_depth_3(self):
        # GIVEN: 1 control submission and one submission with comment tree
        reddit_mock = self.mock_factory.get(comment_tree=True)
        self.request_content["comment_depth"] = "3"
        request_instance = RequestHandler(self.request_content,self.database_mock,reddit_mock,self.logger)

        # WHEN
        request_instance.run()

        # THEN: Expect to not find "level 4" in text
        self.assertFalse("level 4" in self.database_mock.get_text())


    # TODO add asserts
    def test_request_comment_depth_all(self):
        # GIVEN: 1 control submission and one submission with comment tree
        reddit_mock = self.mock_factory.get(comment_tree=True)
        self.request_content["comment_depth"] = "6"
        request_instance = RequestHandler(self.request_content,self.database_mock,reddit_mock,self.logger)

        # WHEN
        request_instance.run()

        # THEN: Expect to not find url in text
        self.assertTrue("level 4" in self.database_mock.get_text())


    def test_request_comment_depth_none(self):
        # GIVEN: 1 control submission and one submission with comment tree
        reddit_mock = self.mock_factory.get(comment_tree=True)
        self.request_content["comment_depth"] = "0"
        request_instance = RequestHandler(self.request_content,self.database_mock,reddit_mock,self.logger)

        # WHEN
        request_instance.run()

        # THEN: Expect to not find url in text
        self.assertFalse("Comment" in self.database_mock.get_text())


if __name__ == '__main__':
    unittest.main()
