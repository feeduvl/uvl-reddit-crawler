import re
import emoji
 
from datetime import datetime


class SubmissionWrapper:
    def __init__(self, timeframe) -> None:
        self.timeframe = timeframe
        self.comment_length = -1
        self.post_length = -1
        self.comment_level = -1
        self.blacklist_comments = []
        self.blacklist_posts = []
        self.replace_urls = ""
        self.replace_emojis = ""

    def set_minimum_lengths(self, comment_length="", post_length=""):
        if comment_length.isnumeric():
            self.comment_length = int(comment_length)
        if post_length.isnumeric():
            self.post_length = int(post_length)

    def set_comment_depth(self, comment_depth):
        if comment_depth.isnumeric():
            self.comment_level = int(comment_depth)

            # level = 6 means no depth limit
            if self.comment_level == 6:
                self.comment_level = -1

    def set_blacklists(self, list_comments=[], list_posts=[]):
        self.blacklist_comments =  list_comments
        self.blacklist_posts = list_posts

    def set_special_char_filtering(self, replace_urls=False, replace_emojis=False):
        # add check if parameter was supplied and if replacement is necessary
        self.replace_urls = replace_urls
        self.replace_emojis = replace_emojis

    def create(self, submission):
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
                    checked_comments.append(comment.body)
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

    def __process_string(self, string):
        if self.replace_urls:
            string = self.__replace_urls(string)
        if self.replace_emojis:
            string = self.__replace_special_chars(string)
        return string

    def __replace_urls(self, textbody):
        url_regex = r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))'''
        return re.sub(url_regex, "", textbody)

    def __replace_special_chars(self, textbody):
        emoji_regex = emoji.get_emoji_regexp()
        return re.sub(emoji_regex, "", textbody)