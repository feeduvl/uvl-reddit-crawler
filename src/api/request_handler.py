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

        min_length_comments = int(self.request_content["min_length_comments"])
        min_length_posts    = int(self.request_content["min_length_posts"])
        comment_depth       = int(self.request_content["comment_depth"])

        blacklist_posts    = self.request_content["blacklist_posts"]
        blacklist_comments = self.request_content["blacklist_comments"]


        replace_urls   = self.request_content["replace_urls"]
        replace_emojis = self.request_content["replace_emojis"]

        for index, subreddit in enumerate(subreddits):
            reddit_crawler = RedditCrawler(self.reddit_instance, self.logger)
            reddit_crawler.crawl(subreddit, date_from, date_to, min_length_comments, min_length_posts, comment_depth, blacklist_posts, blacklist_comments, replace_urls, replace_emojis)

            if index < len(collection_names):
                collection_name = collection_names[index]
            else:
                collection_name = f'{subreddit}_{date_from}_{date_to}'

            crawled_documents = reddit_crawler.get_documents(collection_name)

            self.database_handler.insert(collection_name, crawled_documents)
