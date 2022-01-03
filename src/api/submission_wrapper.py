import praw
import re
 
from datetime import datetime
#from utils import Timeframe


class SubmissionWrapper:
    def __init__(self, timeframe) -> None:
        self.timeframe = timeframe
        self.comment_length = -1
        self.post_length = -1
        self.comment_level = -1
        self.blacklist_comments = []
        self.blacklist_posts = []
        self.url_placeholder = ""
        self.special_char_placeholder = ""

    def set_minimum_lengths(self, comment_length=-1, post_length=-1):
        self.comment_length = comment_length
        self.post_length = post_length

    def set_blacklists(self, list_comments=[], list_posts=[]):
        self.blacklist_comments =  list_comments
        self.blacklist_posts = list_posts

    def set_placeholders(self, url_placeholder="", char_placeholder=""):
        # add check if parameter was supplied and if replacement is necessary
        self.url_placeholder = url_placeholder
        self.special_char_placeholder = char_placeholder

    def create(self, submission):
        self.valid = True
        self.title = self.__check_title(submission.title)
        self.selftext = self.__check_selftext(submission.selftext)
        self.comments = self.__check_comments(submission.comments.list())
        #self.comments = self.__check_comments_with_level(submission)

    def __check_title(self, title):
        return title

    def __check_selftext(self, selftext):
        if self.url_placeholder != "": #refine
            selftext = self.__replace_urls(selftext)
        if len(selftext) < self.post_length and self.post_length >= 0:
            self.valid = False
            return selftext
        for blacklisted_word in self.blacklist_posts:
            if blacklisted_word in selftext:
                self.valid = False
                return selftext
        return selftext

    def __check_comments(self,comments):
        checked_comments = []
        for comment in comments:       # pythonic refactoring required
            comment_valid = True
            try:
                if len(comment.body) < self.comment_length and self.comment_length >= 0:
                    comment_valid = False
                for blacklisted_word in self.blacklist_comments:
                    if blacklisted_word in comment.body:
                        comment_valid = False
                if comment_valid:
                    checked_comments.append(comment.body)
            except AttributeError:
                continue
        return checked_comments

    def __check_comments_with_level(self,submission):
        check_comments = []
        comment_level = 1

        submission.comments.replace_more(limit=None)
        comment_queue = submission.comments[:]  # Seed with top-level

        comments_exist = True
        while comments_exist:
            next_level_comments = []
            for comment in comment_queue:
                check_comments.append(f'comment lvl {comment_level}: {comment.body}')
                next_level_comments.extend(comment.replies)
            if len(next_level_comments) > 0:
                comment_queue = next_level_comments
                comment_level += 1
            else:
                comments_exist = False
        return check_comments


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
            submission_comments.append(comment)
        return submission_title, submission_text, submission_comments

    def get(self):
        documents = []
        submission_title, submission_text, submission_comments = self.__get_submission_data()
        document = { "title": submission_title, "text": submission_text, "comments" : submission_comments }
        documents.append(document)
        return document

    def __replace_urls(self, textbody):
        # https://stackoverflow.com/questions/6038061/regular-expression-to-find-urls-within-a-string
        url_regex = "(?:(?:https?|ftp|file):\/\/|www\.|ftp\.)(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[A-Z0-9+&@#\/%=~_|$])"
        return re.sub(url_regex, self.url_placeholder, textbody)

    def __replace_special_chars(self, textbody):
        return re.sub("TODO", "TODO", textbody)