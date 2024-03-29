from src.api.crawler import RedditCrawler

class RequestHandler:
    def __init__(self, request_content, database_handler, reddit_instance, logger) -> None:
        """Constructor of RequestHandler        
        """
        self.request_content = request_content
        self.database_handler = database_handler
        self.reddit_instance = reddit_instance
        self.logger = logger

    def run(self):
        """Method to orchestrate crawler runs for a given request        
        """
        subreddits = self.request_content["subreddits"]
        dataset_name = self.request_content["dataset_name"]
        date_from = self.request_content["date_from"]
        date_to = self.request_content["date_to"]
        post_selection = self.request_content["post_selection"]
        new_limit = int(self.request_content["new_limit"])

        min_length_comments = int(self.request_content["min_length_comments"])
        min_length_posts = int(self.request_content["min_length_posts"])
        comment_depth = int(self.request_content["comment_depth"])

        blacklist_posts = self.request_content["blacklist_posts"]
        blacklist_comments = self.request_content["blacklist_comments"]

        replace_urls = self.request_content["replace_urls"]
        replace_emojis = self.request_content["replace_emojis"]

        crawled_documents = []
        for index, subreddit in enumerate(subreddits):
            self.logger.info(f'Starting crawl of {subreddit}')
            reddit_crawler = RedditCrawler(self.reddit_instance, self.logger)
            reddit_crawler.crawl(subreddit, date_from, date_to, post_selection, new_limit, min_length_comments, min_length_posts, comment_depth, blacklist_posts, blacklist_comments, replace_urls, replace_emojis)

            crawled_documents += reddit_crawler.get_documents(subreddit)

        self.database_handler.insert(dataset_name, crawled_documents, self.logger)
