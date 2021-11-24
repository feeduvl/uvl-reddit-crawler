import praw
import pymongo
from datetime import date, datetime
from utils import Utils


class RedditCrawler:
    def __init__(self, reddit_instance, database_client) -> None:
        self.reddit = reddit_instance
        self.database_client = database_client
        self.utilities = Utils()

    def __get_submission_data(self,submission):
        submission_title = submission.title
        submission_text = submission.selftext
        submission_comments = []
        for comment in submission.comments.list():
            try:
                submission_comments.append(comment.body)
            except AttributeError:
                continue
        return submission_title, submission_text, submission_comments
    
    def crawl(self, subreddit_name, from_date_str, to_date_str):
        subreddit = self.reddit.subreddit(subreddit_name)
        db_column = self.database_client[subreddit_name]
        from_date = datetime.strptime(from_date_str, "%d%m%Y").date()
        to_date   = datetime.strptime(to_date_str, "%d%m%Y").date()    
        documents = []

        for submission in subreddit.top(self.utilities.get_time_qualifier(from_date)):
#            submission_date = datetime.utcfromtimestamp(int(submission.created_utc)).strftime('%Y-%m-%d %H:%M:%S')
            submission_date = datetime.utcfromtimestamp(int(submission.created_utc)).date()
            
            if self.utilities.in_timeframe(submission_date,from_date,to_date):
                submission_title, submission_text, submission_comments = self.__get_submission_data(submission)
                document = { "title": submission_title, "text": submission_text, "comments" : submission_comments }
                documents.append(document)
        
        db_column.insert_many(documents)
        pass


class DBColumnMock:
    def insert_many(self,documents):
        print(" Objects found")
        for document in documents:
            print(" --- ")
            print(document["title"])
            print(document["text"])
            for comment in document["comments"]:
                print(comment)

class DBMock:
    def __getitem__(self,arg):
        return DBColumnMock()



if __name__ == "__main__":
    reddit = praw.Reddit(
        client_id="P0eMVNdwpy29g3K2LhCPTw",
        client_secret="9s-TrT5HJASoawBN951QWsUQTck-mg",
        user_agent="script:api_test:v1.0.0 (by u/uvl_reddit_crawler)",
    )

    database_client = DBMock()
    crawler = RedditCrawler(reddit, database_client)
    
    crawler.crawl("vim", "13112021", "23112021")
    print("end")