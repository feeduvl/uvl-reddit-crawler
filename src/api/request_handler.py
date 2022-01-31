from src.api.crawler import RedditCrawler

class RequestHandler:
    def __init__(self, request_content, database_handler, reddit_instance, logger) -> None:
        self.request_content = request_content
        self.database_handler = database_handler
        self.reddit_instance = reddit_instance
        self.logger = logger

    def run(self):
        subreddits = self.request_content["subreddits"]
        collection_names = self.request_content["collection_names"]
        date_from  = self.request_content["date_from"]
        date_to    = self.request_content["date_to"]

        min_length_comments = self.request_content["min_length_comments"]
        min_length_posts = self.request_content["min_length_posts"]

        blacklist_posts    = self.request_content["blacklist_posts"]
        blacklist_comments = self.request_content["blacklist_comments"]
        
        for index, subreddit in enumerate(subreddits):
            reddit_crawler = RedditCrawler(self.reddit_instance, self.logger)
            reddit_crawler.crawl(subreddit, date_from, date_to, min_length_comments, min_length_posts, blacklist_posts, blacklist_comments)

            if index < len(collection_names):
                collection_name = collection_names[index]
            else:
                collection_name = f'{subreddit}_{date_from}_{date_to}'

            crawled_documents = reddit_crawler.get_documents(collection_name)

            self.database_handler.insert(collection_name, crawled_documents)
        pass