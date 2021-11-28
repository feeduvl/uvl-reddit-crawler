import praw
import pymongo
import logging
from datetime import date, datetime
from utils import Utils, Timeframe
from preprocessor import PreprocessingEngine
from submission_wrapper import SubmissionWrapper

class RedditCrawler:
    def __init__(self, reddit_instance, database_client, preprocessor) -> None:
        self.reddit = reddit_instance
        self.database_client = database_client
        self.preprocessor = preprocessor
        self.utilities = Utils()

    
    def crawl(self, subreddit_name, from_date_str, to_date_str):
        subreddit = self.reddit.subreddit(subreddit_name)
        db_column = self.database_client[subreddit_name]
        from_date = datetime.strptime(from_date_str, "%d%m%Y").date()
        to_date   = datetime.strptime(to_date_str, "%d%m%Y").date()    
        timeframe = Timeframe(from_date,to_date)
        
        accept_counter = 0
        documents = []
        
        for submission_counter, submission in enumerate(subreddit.top(self.utilities.get_time_qualifier(from_date))):
            submission_wrapped = SubmissionWrapper(submission,timeframe)
            
            if submission_wrapped.valid:
                documents.append(submission_wrapped.get())
                accept_counter += 1

        logging.info(f'Number of submissions found:    {submission_counter+1}')
        logging.info(f'Number of submissions accepted: {accept_counter}')

        # buffering?        
        db_column.insert_many(documents)
        pass


class DBColumnMock:
    def insert_many(self,documents):
        print(f'Objects found: {len(documents)}')
        for document in documents:
            print("-----------------------------------------------------------------------")
            print(f'Submission: {document["title"]}')
            print("-----------------------------------------------------------------------")
            print(document["text"])
            for index, comment in enumerate(document["comments"]):
                print(f'Comment No. {index+1}')
                print(comment)

class DBMock:
    def __getitem__(self,arg):
        return DBColumnMock()



if __name__ == "__main__":
    start_time = datetime.now()
    
    reddit = praw.Reddit(
        client_id="P0eMVNdwpy29g3K2LhCPTw",
        client_secret="9s-TrT5HJASoawBN951QWsUQTck-mg",
        user_agent="script:api_test:v1.0.0 (by u/uvl_reddit_crawler)",
    )

    database_client = DBMock()
    preprocessor = PreprocessingEngine()
    crawler = RedditCrawler(reddit, database_client, preprocessor)
    subreddit = "vim"
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