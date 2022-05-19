"""This module contains coding for submission processing that extends the praw
crawling capabilities
"""
import re
from datetime import datetime
import emoji
import os

class SubmissionWrapper:
    """Wrapper class for praw.submission that contains preprocessing logic needed

    Optional preprocessing steps:
    Length filtering for submission texts and comments,
    comment reply depth limiting, blacklist for submission texts and and comments,
    an option to remove emojis and urls from submission texts and comments
    """
    def __init__(self, timeframe) -> None:
        self.timeframe = timeframe
        self.comment_length = -1
        self.post_length = -1
        self.comment_level = -1
        self.blacklist_comments = []
        self.blacklist_posts = []
        self.replace_urls = ""
        self.replace_emojis = ""

        self.valid = True
        self.title = ''
        self.selftext = ''
        self.comments = []

    def set_minimum_lengths(self, comment_length=None, post_length=None):
        """Setter method for minumum lengths"""
        if comment_length is not None:
            self.comment_length = comment_length
        if post_length is not None:
            self.post_length = post_length

    def set_comment_depth(self, comment_depth):
        """Setter method for maximum comment reply depth"""
        self.comment_level = comment_depth

        # level = 6 means no depth limit
        if self.comment_level == 6:
            self.comment_level = -1

    def set_blacklists(self, list_comments=None, list_posts=None):
        """Setter method for the comment and text body blacklists"""
        if list_comments is None:
            self.blacklist_comments = []
        else:
            self.blacklist_comments = list_comments
        if list_posts is None:
            self.blacklist_posts = []
        else:
            self.blacklist_posts = list_posts

    def set_special_char_filtering(self, replace_urls=False, replace_emojis=False):
        """Setter method for filtering of urls and emojis"""
        # add check if parameter was supplied and if replacement is necessary
        self.replace_urls = replace_urls
        self.replace_emojis = replace_emojis

    def create(self, submission):
        """Create the submission by running all checks"""
        self.valid = True
        self.__check_submission(submission)
        self.title = self.__check_title(submission.title)
        self.selftext = self.__check_selftext(submission.selftext)
#        self.comments = self.__check_comments(submission.comments.list())
        self.comments = self.__check_comments_with_level(submission)

    def __check_title(self, title):
        title = self.__process_string(title)
        return title

    def __check_selftext(self, selftext):
        selftext = self.__process_string(selftext)

        if len(selftext) < self.post_length and self.post_length >= 0:
            self.valid = False
            return selftext
        for blacklisted_word in self.blacklist_posts:
            if blacklisted_word in selftext:
                self.valid = False
                return selftext
        return selftext

    def __check_comments_with_level(self,submission):
        checked_comments = []
        comment_level = 1

        submission.comments.replace_more(limit=None)
        comment_queue = submission.comments[:]
        # search comment tree for comments
        more_comments_exist = True
        comment_is_valid = True
        while more_comments_exist:
            # exit if max level has been reached
            if comment_level-1 >= self.comment_level and self.comment_level >= 0:
                break

            next_level_comments = []

            # process all comments of a specific level
            for comment in comment_queue:
                processed_comment = self.__process_string(comment.body)
                comment_is_valid = not (len(processed_comment) < self.comment_length and self.comment_length >= 0)
                for blacklisted_word in self.blacklist_comments:
                    if blacklisted_word in processed_comment:
                        comment_is_valid = False

                if comment_is_valid:
                    checked_comments.append(processed_comment)
                    # if a comment is not valid replies will be discarded
                    next_level_comments.extend(comment.replies)

            # go down one level if more comments exist
            if len(next_level_comments) > 0:
                comment_queue = next_level_comments
                comment_level += 1
            else:
                more_comments_exist = False

        return checked_comments

    def __check_submission(self,submission):
        submission_date = datetime.utcfromtimestamp(int(submission.created_utc)).date()
        if not self.timeframe.is_in_timeframe(submission_date):
            self.valid = False

    def __get_submission_data(self):
        submission_title = self.title
        submission_text = self.selftext
        submission_comments = []
        for comment in self.comments:
            submission_comments.append(comment)
        return submission_title, submission_text, submission_comments

    def get(self):
        """Returns the processed submission"""
        documents = []
        submission_title, submission_text, submission_comments = self.__get_submission_data()
        document = { "title": submission_title, "text": submission_text, "comments" : submission_comments }
        documents.append(document)
        return document

    def __process_string(self, string):
        string = self.__replace_linebreaks(string)
        if self.replace_urls:
            string = self.__replace_urls(string)
        if self.replace_emojis:
            string = self.__replace_special_chars(string)
        return string

    def __replace_urls(self, textbody):
        url_regex_https = r'(https?://\S+)'
        cleaned_text = re.sub(url_regex_https, '', textbody)
        url_regex = r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
        return re.sub(url_regex, '', cleaned_text)

    def __replace_special_chars(self, textbody):
        return emoji.get_emoji_regexp().sub('', textbody)

    def __replace_linebreaks(self,text):
        return text.replace(os.linesep,' ')
