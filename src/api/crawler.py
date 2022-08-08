"""This module contains the crawling orchestration."""
from datetime import datetime
import os
from src.api.utils import Utils, Timeframe
from src.api.submission_wrapper import SubmissionWrapper

class RedditCrawler:
    """This class handles API calls to the praw reddit API."""
    def __init__(self, reddit_instance, logger) -> None:
        self.reddit = reddit_instance
        self.utilities = Utils()
        self.crawled_data = []
        self.logger = logger


    def crawl(self, subreddit_name, from_date_str, to_date_str, post_selection, new_limit,
              min_length_comments=0, min_length_posts=0, comment_depth=1,
              blacklist_comments=None, blacklist_posts=None,
              replace_urls=False,replace_emojis=False):
        """Initiate a crawling job for the specified subreddit using an
        optional number of preprocessing parameters
        """
        subreddit = self.reddit.subreddit(subreddit_name)
        
        # date in MM/DD/YYYY
        from_date = datetime.strptime(from_date_str, "%m/%d/%Y").date()
        to_date = datetime.strptime(to_date_str, "%m/%d/%Y").date()
        timeframe = Timeframe(from_date,to_date)

        submission_wrapped = SubmissionWrapper(timeframe)
        submission_wrapped.set_minimum_lengths(min_length_comments, min_length_posts)
        submission_wrapped.set_comment_depth(comment_depth)
        submission_wrapped.set_blacklists(blacklist_comments,blacklist_posts)
        submission_wrapped.set_special_char_filtering(replace_urls,replace_emojis)

        accept_counter = 0
        submission_counter = 0

        self.logger.info(f'Getting posts from {subreddit_name}, post selection: {post_selection}')
        if post_selection == 'top':
            self.logger.info('Sorting by top')
            submissions = subreddit.top(self.utilities.get_time_qualifier(from_date))
        else:
            self.logger.info('Sorting by new')
            submissions = subreddit.new(limit=new_limit)

        for submission_counter, submission in enumerate(submissions):
            submission_wrapped.create(submission)

            if submission_wrapped.valid:
                self.crawled_data.append(submission_wrapped.get())
                accept_counter += 1

        self.logger.info(f'Number of submissions found:    {submission_counter+1}')
        self.logger.info(f'Number of submissions accepted: {accept_counter}')


    def get_documents(self, collection_name):
        """Getter method for the data that is obtained in a crawling run.

        The data is return in a dictionary: {"id": ..., "text": ...}. Text and comments of a post begins with '###'.
        """
        documents = []
        sep = os.linesep + '###'
        date = datetime.today().strftime('%Y_%m_%d')
        for index, dataset in enumerate(self.crawled_data):
            document_id = f'{collection_name}_{str(index)}_{date}'
            text = dataset.get("title") + sep + dataset.get("text") + sep + sep.join(dataset.get("comments"))
            documents.append({"id": document_id, "text": text})
        return documents
