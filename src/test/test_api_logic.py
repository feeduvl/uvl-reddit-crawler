import unittest
from unittest.mock import MagicMock
import datetime
import os

# https://gideonbrimleaf.github.io/2021/01/26/relative-imports-python.html
import sys
sys.path.append("..")

#from utils import Utils, Timeframe
#from submission_wrapper import SubmissionWrapper
from src.api.utils import Utils, Timeframe
from src.api.submission_wrapper import SubmissionWrapper

class TestUtils(unittest.TestCase):
    
    def setUp(self) -> None:
        self.today = datetime.date.today()
        self.utils_instance = Utils()
        self.timeframe_instance = Timeframe(self.today - datetime.timedelta(days=15),self.today - datetime.timedelta(days=5))
        pass

    def test_time_qualifier_days_zero(self):        
        from_date = self.today
        qualifier = self.utils_instance.get_time_qualifier(from_date)
        self.assertEqual(qualifier, "day", "classification for 0 days difference")

    def test_time_qualifier_days_5(self):        
        from_date = self.today - datetime.timedelta(days=5)
        qualifier = self.utils_instance.get_time_qualifier(from_date)
        self.assertEqual(qualifier, "week", "classification for 5 days difference")

    def test_time_qualifier_days_7(self):        
        from_date = self.today - datetime.timedelta(days=7)
        qualifier = self.utils_instance.get_time_qualifier(from_date)
        self.assertEqual(qualifier, "week", "classification for 7 days difference")

    def test_time_qualifier_days_8(self):        
        from_date = self.today - datetime.timedelta(days=8)
        qualifier = self.utils_instance.get_time_qualifier(from_date)
        self.assertEqual(qualifier, "month", "classification for 8 days difference")

    def test_time_qualifier_days_32(self):        
        from_date = self.today - datetime.timedelta(days=32)
        qualifier = self.utils_instance.get_time_qualifier(from_date)
        self.assertEqual(qualifier, "year", "classification for 32 days difference")

    def test_time_qualifier_days_366(self):        
        from_date = self.today - datetime.timedelta(days=366)
        qualifier = self.utils_instance.get_time_qualifier(from_date)
        self.assertEqual(qualifier, "all", "classification for 366 days difference")

    def test_timeframe_accept(self):
        #from_date = self.today - datetime.timedelta(days=10)
        test_date = self.today - datetime.timedelta(days=10)
        decision = self.timeframe_instance.is_in_timeframe(test_date)
        self.assertEqual(decision, True, "Test date in timeframe")

    def test_timeframe_discard(self):
        #from_date = self.today - datetime.timedelta(days=10)
        test_date = self.today - datetime.timedelta(days=20)
        decision = self.timeframe_instance.is_in_timeframe(test_date)
        self.assertEqual(decision, False, "Test date out of timeframe")


class TestPreprocessing(unittest.TestCase):
    title_long            = "this is a title of a reddit submission"
    submission_text_long  = "this is the textbody of a reddit submission which is longer than 20 characters"
    blacklist_word        = "abcdefg"
    submission_text_med   = "this is the textbody of a reddit submission which contains a blacklisted word: " + blacklist_word
    submission_text_short = "too short"
    submission_line_break = f'this is sufficiently long submission text{os.linesep}that contains a line break'
    submission_text_url = "this is a submission text that contains the URL https://www.reddit.com/ for replacing"
    submission_text_emoji = 'emojis: 🙈🤷 .'
    comments_all_valid    = ["comment A", "comment B", "comment C"]
    comments_two_valid    = ["comment A", "---", "comment C"]
    comments_blacklist    = ["comment A", blacklist_word, "comment C"]
    comments_line_breaks  = [f'comment A{os.linesep}new line', "comment B without linebreak"]

    def setUp(self) -> None:
        self.timeframe_mock = MagicMock()
        self.timeframe_mock.is_in_timeframe.return_value(True)
        pass

    def __get_submission_mock(self,title,text,comments):
        submission_mock = MagicMock()
        submission_mock.title = title
        submission_mock.selftext = text
        submission_mock.created_utc = "0"

        # pythonic refactoring required
        comments_mock_return_list = []
        for comment in comments:
            comment_mock = MagicMock()
            comment_mock.body = comment
            comment_mock.replies = []
            comments_mock_return_list.append(comment_mock)

        comments_mock = MagicMock()
        comments_mock.__getitem__.return_value = comments_mock_return_list

        submission_mock.comments = comments_mock
        return submission_mock

    def test_submission_valid(self):
        submission_mock = self.__get_submission_mock(title=self.title_long,text=self.submission_text_long,comments=self.comments_all_valid)

        submission_wrapper_instance = SubmissionWrapper(self.timeframe_mock)
        submission_wrapper_instance.create(submission_mock)
        self.assertTrue(submission_wrapper_instance.valid)

    def test_submission_invalid(self):
        submission_mock = self.__get_submission_mock(title=self.title_long,text=self.submission_text_short,comments=self.comments_all_valid)

        submission_wrapper_instance = SubmissionWrapper(self.timeframe_mock)
        submission_wrapper_instance.set_minimum_lengths(post_length=20)
        submission_wrapper_instance.create(submission_mock)
        self.assertFalse(submission_wrapper_instance.valid)


    def test_comment_filter(self):
        submission_mock = self.__get_submission_mock(title=self.title_long,text=self.submission_text_long,comments=self.comments_two_valid)
        
        submission_wrapper_instance = SubmissionWrapper(self.timeframe_mock)
        submission_wrapper_instance.set_minimum_lengths(comment_length=5)
        submission_wrapper_instance.create(submission_mock)
        self.assertEqual(len(submission_wrapper_instance.comments),2, f'Comment filtering failed: {submission_wrapper_instance.comments}')

    def test_blacklisting_post(self):
        submission_mock = self.__get_submission_mock(title=self.title_long,text=self.submission_text_med,comments=self.comments_all_valid)
        
        submission_wrapper_instance = SubmissionWrapper(self.timeframe_mock)
        submission_wrapper_instance.set_blacklists(list_posts=[self.blacklist_word])
        submission_wrapper_instance.create(submission_mock)
        self.assertFalse(submission_wrapper_instance.valid)

    def test_blacklisting_comment(self):
        submission_mock = self.__get_submission_mock(title=self.title_long,text=self.submission_text_long,comments=self.comments_blacklist)
        
        submission_wrapper_instance = SubmissionWrapper(self.timeframe_mock)
        submission_wrapper_instance.set_blacklists(list_comments=[self.blacklist_word])
        submission_wrapper_instance.create(submission_mock)
        self.assertEqual(len(submission_wrapper_instance.comments),2, f'Comment blacklisting failed: {submission_wrapper_instance.comments}')
        
    def test_url_replacing(self):
        replace_string = "https://bugzilla.mozilla.org/show_bug.cgi?id=1752466"
        submission_mock = self.__get_submission_mock(title=self.title_long,text=self.submission_text_url,comments=self.comments_all_valid)

        submission_wrapper_instance = SubmissionWrapper(self.timeframe_mock)
        submission_wrapper_instance.set_special_char_filtering(replace_urls=True)
        submission_wrapper_instance.create(submission_mock)

        self.assertFalse(replace_string in submission_wrapper_instance.selftext, f'URL replacing failed: {submission_wrapper_instance.selftext}')

    def test_emoji_replacing(self):
        replace_string = "🙈🤷"
        submission_mock = self.__get_submission_mock(title=self.title_long,text=self.submission_text_emoji,comments=self.comments_all_valid)

        submission_wrapper_instance = SubmissionWrapper(self.timeframe_mock)
        submission_wrapper_instance.set_special_char_filtering(replace_emojis=True)
        submission_wrapper_instance.create(submission_mock)
        self.assertFalse(replace_string in submission_wrapper_instance.selftext, f'Emoji replacing failed: {submission_wrapper_instance.selftext}')

    def test_remove_linebreaks_comment(self):
        submission_mock = self.__get_submission_mock(title=self.title_long,text=self.submission_text_emoji,comments=self.comments_line_breaks)

        submission_wrapper_instance = SubmissionWrapper(self.timeframe_mock)
        submission_wrapper_instance.create(submission_mock)
        print(submission_wrapper_instance.comments[0])
        self.assertFalse(os.linesep in submission_wrapper_instance.comments[0])

    def test_remove_linebreaks_comment(self):
        submission_mock = self.__get_submission_mock(title=self.title_long,text=self.submission_line_break,comments=self.comments_all_valid)

        submission_wrapper_instance = SubmissionWrapper(self.timeframe_mock)
        submission_wrapper_instance.create(submission_mock)
        print(submission_wrapper_instance.selftext)
        self.assertFalse(os.linesep in submission_wrapper_instance.selftext)



if __name__ == '__main__':
    unittest.main()