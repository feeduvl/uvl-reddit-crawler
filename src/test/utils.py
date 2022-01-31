import os
from unittest.mock import MagicMock


class CommentMock:
    def __init__(self,body) -> None:
        self.body = body
        pass

class SubmissionMock:
    def __init__(self, comments, date, title, text) -> None:
        self.title = title
        self.selftext = text
        self.comments = MagicMock()
        self.comments.list.return_value = comments
        self.created_utc = date
        pass

class SubredditMock:
    def __init__(self,submissions=[]) -> None:
        self.submissions = submissions
        pass

    def top(self, timeframe=''):
        return self.submissions 

class RedditMock:
    def __init__(self,subreddit) -> None:
        self.subreddit_mock = subreddit
        pass

    def subreddit(self,name=''):
        return self.subreddit_mock


class RedditMockFactory():
    title                 = "this is a title of a reddit submission"
    title_short           = "too short"
    submission_text       = "this is the textbody of a reddit submission which is longer than 20 characters"
    submission_text_short = "too short"
    blacklist_word        = "<word>"
    url_string            = "this is a submission text that contains the URL https://www.reddit.com/ for replacing"
    emoji_string          = "🙈"
    comments_all_valid    = ["comment A", "comment B", "comment C"]
    comment_url           = ["comment https://www.reddit.com/"]
    date_valid            = '1643188166' # 2022-01-26
    date_invalid          = '1642793826' # 2022-01-21


    def __init__(self) -> None:
        pass

    def get(self,short_title=False,short_submission=False,blacklist_used=False,date_invalid=False,contains_emoji=False,contains_url=False):
        # refactoring needed

        # build comment mock
        comment_list = []
        for comment in self.comments_all_valid:
            comment_mock = CommentMock(comment)
            comment_list.append(comment_mock)

        # build submission mock
        if not date_invalid:
            date = self.date_valid
        else:
            date = self.date_invalid
        
        if short_submission:
            submission_text = self.submission_text_short
        else:
            submission_text = self.submission_text

        if blacklist_used:
            submission_text += f' {self.blacklist_word}'
        
        if contains_url:
            submission_text += f' {self.url_string}'

        if contains_emoji:
            submission_text += f' {self.emoji_string}'

        if short_title:
            title = self.title_short
        else:
            title = self.title

        submission_mock = SubmissionMock(comment_list, date, title, submission_text)        
        
        # wrap submission in other classes
        control_submission = self.__get_control_submission()
        subreddit_mock = SubredditMock([control_submission,submission_mock])
        reddit_mock = RedditMock(subreddit_mock)

        # generate expected crawling result
        sep = os.linesep
        crawling_result = title + sep + submission_text + sep + sep.join(self.comments_all_valid)

        return reddit_mock, crawling_result

    def __get_control_submission(self):
        comment_list = []
        for comment in self.comments_all_valid:
            comment_mock = CommentMock(comment)
            comment_list.append(comment_mock)

        return SubmissionMock(comment_list, self.date_valid, self.title, self.submission_text)