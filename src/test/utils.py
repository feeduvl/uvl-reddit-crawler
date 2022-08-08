"""This module contains several utility classes for integration tests.

Several classes act as mock classes for the praw reddit API and can
be accessed either directly or using the reddit mock factory. There
is an additional class that can be used a mock for the database
handling.
"""
from unittest.mock import MagicMock


class CommentMock:
    """Mock class of a single comment.

    If a comment tree is expected, the attribute replies can be used to store
    another instance of CommentMock. This creates the nested comment structure
    that is expectd by the API's comment depth algorithm."""
    def __init__(self,body,replies=None) -> None:
        self.body = body
        if replies is None:
            self.replies = []
        else:
            self.replies = replies


class SubmissionMock:
    """This class mocks the submission class of the praw reddit API.

    The comments of submission can be accessed using getitem.
    """
    def __init__(self, comments, date, title, text) -> None:
        self.title = title
        self.selftext = text
        self.comments = MagicMock()
        self.comments.__getitem__.return_value = comments
        self.created_utc = date


class SubredditMock:
    """This class mocks the subreddit class of the praw reddit API.

    The submissions have to be set in the constructor. The submissions can be
    accessed using the top method.
    """
    def __init__(self,submissions=None) -> None:
        if submissions is None:
            self.submissions = []
        else:
            self.submissions = submissions

    def top(self, timeframe=''):
        """This method is a getter for the stored submission mocks."""
        return self.submissions 


class RedditMock:
    """This class is a mock of the reddit class and is used a the central
    entry point to the API classes. This class contains all other mock
    classes.
    """
    def __init__(self,subreddit) -> None:
        self.subreddit_mock = subreddit

    def subreddit(self,name=''):
        """This method returns the subreddit mock class."""
        return self.subreddit_mock


class RedditMockFactory():
    """The reddit mock factory returns a class instance that can be used
    as a mock for praw.reddit. All class attributes are mocked in such a
    way to be consumed by the feed.uvl crawling API.

    A selection of parameters can be used to created different test scenarios.
    """
    title = "this is a title of a reddit submission"
    submission_text = "this is the textbody of a reddit submission which is longer than 20 characters"
    text_short = "too short"
    blacklist_word = "<word>"
    url_string = "https://support.mozilla.org/en-US/kb/how-disable-enterprise-roots-preference"
    emoji_string = "🙈"
    comments_all_valid = ["long comment A", "valid comment B", "another comment C"]
    comment_url = ["comment https://www.reddit.com/"]
    date_valid = '1643188166' # 2022-01-26
    date_invalid = '1642793826' # 2022-01-21


    def __init__(self) -> None:
        pass

    def get(self,short_submission=False,blacklist_in_post=False,blacklist_in_comment=False,short_comment=False,
            date_invalid=False,contains_emoji=False,contains_url=False,comment_tree=False):
        """Get a mock instance of praw.reddit with the specified properties.

        The returned instance will contain two submission instance. The first
        instance is a control submission that will no be changed by the
        parameters. The second submissions is supposed to be used as test
        result.
        """
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

        return reddit_mock

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
        level_1_comment_a = CommentMock("Comment A with level 1")
        level_1_comment_b = CommentMock("Comment B with level 1")

        level_2_comment_c = CommentMock("Comment C with level 2")
        level_2_comment_d = CommentMock("Comment D with level 2")
        level_2_comment_e = CommentMock("Comment E with level 2")

        level_3_comment_f = CommentMock("Comment F with level 3")
        level_3_comment_g = CommentMock("Comment G with level 3")

        level_4_comment_h = CommentMock("Comment H with level 4")

        level_3_comment_g.replies = [level_4_comment_h]
        level_2_comment_c.replies = [level_3_comment_f, level_3_comment_g]
        level_1_comment_a.replies = [level_2_comment_c, level_2_comment_d]

        level_1_comment_b.replies = [level_2_comment_e]

        return [level_1_comment_a,level_1_comment_b]


class DBHandlerMock:
    """Mock class of DatabaseHandler in api/utils/ for test result capturing.
    """
    def __init__(self) -> None:
        self.documents = []
        self.dataset_name = ''

    def get_documents(self):
        """Returns captured documents."""
        return self.documents

    def insert(self, dataset_name, documents):
        """Perform a mock insert and store the data in class
        attributes.
        """
        self.documents.append(documents)
        self.dataset_name = dataset_name

    def get_text(self):
        """Return the text column of the captured crawling result of
        the non-control submission.
        """
        return self.get_documents()[0][1].get('Text')
