import praw
import pymongo
import logging
from datetime import date, datetime
from src.api.utils import Utils, Timeframe
from src.api.submission_wrapper import SubmissionWrapper

class RedditCrawler:
    def __init__(self, reddit_instance, database_client) -> None:
        self.reddit = reddit_instance
        self.database_client = database_client
        self.utilities = Utils()

    
    def crawl(self, subreddit_name, from_date_str, to_date_str, min_length_comments=0, min_length_posts=0, blacklist_comments=[], blacklist_posts=[]):
        subreddit = self.reddit.subreddit(subreddit_name)
        db_column = self.database_client[subreddit_name]
        from_date = datetime.strptime(from_date_str, "%d%m%Y").date()
        to_date   = datetime.strptime(to_date_str, "%d%m%Y").date()    
        timeframe = Timeframe(from_date,to_date)

        submission_wrapped = SubmissionWrapper(timeframe)
        submission_wrapped.set_minimum_lengths(min_length_comments, min_length_posts)
        submission_wrapped.set_blacklists(blacklist_comments,blacklist_posts)
        
        accept_counter = 0
        documents = []
        
        for submission_counter, submission in enumerate(subreddit.top(self.utilities.get_time_qualifier(from_date))):
            submission_wrapped.create(submission)
            
            if submission_wrapped.valid:
                documents.append(submission_wrapped.get())
                accept_counter += 1

        logging.info(f'Number of submissions found:    {submission_counter+1}')
        logging.info(f'Number of submissions accepted: {accept_counter}')

        db_column.insert_many(documents)
        pass


class DBColumnMock:
    def insert_many(self,documents):
        for document in documents:
            logging.info("-----------------------------------------------------------------------")
            logging.info(f'Submission: {document["title"]}')
            logging.info("-----------------------------------------------------------------------")
            logging.info(document["text"])
            for index, comment in enumerate(document["comments"]):
                logging.info(comment)

class DBMock:
    def __getitem__(self,arg):
        return DBColumnMock()


'''

if __name__ == "__main__":
    start_time = datetime.now()
    
    reddit = praw.Reddit( 
        client_id="",
        client_secret="",
        user_agent="",
    )

    database_client = DBMock()
    crawler = RedditCrawler(reddit, database_client)
    subreddit = "spotify"
    from_date = "13112021"
    to_date = "28112021"

    logging.basicConfig(filename='crawl_info.log', encoding='utf-8', level=logging.INFO, filemode='w')
    logging.info(f'Subreddit: {subreddit}')
    logging.info(f'From Date: {from_date}')
    logging.info(f'To Date:   {to_date}')
    logging.info(f'Crawled at {datetime.today().strftime("%d/%m/%Y")} (DD/MM/YYYY)')
    
    crawler.crawl(subreddit, from_date, to_date)
    elapsed_time = datetime.now()-start_time
    logging.info(f'crawler finished in {elapsed_time}')

'''