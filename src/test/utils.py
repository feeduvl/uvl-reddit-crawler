import os
from unittest.mock import MagicMock


class CommentMock:
    def __init__(self,body,replies=[]) -> None:
        self.body = body
        self.replies = replies
        pass

class SubmissionMock:
    def __init__(self, comments, date, title, text) -> None:
        self.title = title
        self.selftext = text
        self.comments = MagicMock()
        self.comments.list.return_value = comments
        self.comments.__getitem__.return_value = comments
        self.created_utc = date

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
    submission_text       = "this is the textbody of a reddit submission which is longer than 20 characters"
    text_short            = "too short"
    blacklist_word        = "<word>"
    url_string            = "https://www.reddit.com/"
    emoji_string          = "🙈"
    comments_all_valid    = ["long comment A", "valid comment B", "another comment C"]
    comment_url           = ["comment https://www.reddit.com/"]
    date_valid            = '1643188166' # 2022-01-26
    date_invalid          = '1642793826' # 2022-01-21


    def __init__(self) -> None:
        pass

    def get(self,short_submission=False,blacklist_in_post=False,blacklist_in_comment=False,short_comment=False,
            date_invalid=False,contains_emoji=False,contains_url=False,comment_tree=False):
        # refactoring needed

        # build comment mock
        if not comment_tree:
            comment_list = []
            for comment in self.comments_all_valid:
                comment_mock = CommentMock(comment)
                comment_list.append(comment_mock)

            if blacklist_in_comment:
                comment_list[0].body += self.blacklist_word

            if short_comment:
                comment_list[0].body = self.text_short
        else:
            comment_list = self.__get_comment_tree()

        # build submission mock
        if not date_invalid:
            date = self.date_valid
        else:
            date = self.date_invalid
        
        if short_submission:
            submission_text = self.text_short
        else:
            submission_text = self.submission_text

        if blacklist_in_post:
            submission_text += f' {self.blacklist_word}'
        
        if contains_url:
            submission_text += f' {self.url_string}'

        if contains_emoji:
            submission_text += f' {self.emoji_string}'

        submission_mock = SubmissionMock(comment_list, date, self.title, submission_text)        
        
        # wrap submission in other classes
        control_submission = self.__get_control_submission()
        subreddit_mock = SubredditMock([control_submission,submission_mock])
        reddit_mock = RedditMock(subreddit_mock)

        # generate expected crawling result
        sep = os.linesep
        crawling_result = self.title + sep + submission_text + sep + sep.join(self.comments_all_valid)

        return reddit_mock, crawling_result

    def __get_control_submission(self):
        comments = ["comment A of valid post", "control submission valid comment B", "comment C ++++++++++++++++"]
        comment_list = []
        for comment in comments:
            comment_mock = CommentMock(comment)
            comment_list.append(comment_mock)
        
        title = 'title of control submission'
        submission_text = 'submission text of control submission (which also contains a valid number of characters)'

        return SubmissionMock(comment_list, self.date_valid, title, submission_text)

    def __get_comment_tree(self):
        level_1_comment_A = CommentMock("Comment A with level 1")
        level_1_comment_B = CommentMock("Comment B with level 1")
        
        level_2_comment_C = CommentMock("Comment C with level 2")
        level_2_comment_D = CommentMock("Comment D with level 2")
        level_2_comment_E = CommentMock("Comment E with level 2")

        level_3_comment_F = CommentMock("Comment F with level 3")
        level_3_comment_G = CommentMock("Comment G with level 3")

        level_4_comment_H = CommentMock("Comment H with level 4")

        level_3_comment_G.replies = [level_4_comment_H]
        level_2_comment_C.replies = [level_3_comment_F, level_3_comment_G]
        level_1_comment_A.replies = [level_2_comment_C, level_2_comment_D]

        level_1_comment_B.replies = [level_2_comment_E]

        return [level_1_comment_A,level_1_comment_B]

        
