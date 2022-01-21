from flask import Flask, request, json, jsonify
from src.api.crawler import RedditCrawler
from src.api.utils import database_handler
from src.flask_setup import app
import praw
import os

@app.route('/hitec/reddit/crawl', methods=['POST'])
def run_crawler():

    '''
    # Expected example request JSON:

    request_content = {
        "subreddits" : ["ubuntu", "spotify"],
        "from_date" : "13112021",
        "to_date" : "28112021",
        "min_length_comments" : "",
        "min_length_posts" : "",
        "blacklist_comments" : [],
        "blacklist_posts" : [],
    }
    '''
    if request.method == 'POST':
        request_content = request.get_json(force=True)
        app.logger.debug(str(request_content))
    else:
        app.logger.error('Error: Only POST implemented')
        return
    
    reddit = praw.Reddit(
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"],
        user_agent=os.environ["USER_AGENT"],
    )

    database_client = database_handler()

    try:
        subreddits = request_content["subreddits"]
        date_from  = request_content["date_from"]
        date_to    = request_content["date_to"]

        min_length_comments = request_content["min_length_comments"]
        min_length_posts = request_content["min_length_posts"]

        blacklist_posts    = request_content["blacklist_posts"]
        blacklist_comments = request_content["blacklist_comments"]
        
        for subreddit in subreddits:
            reddit_crawler = RedditCrawler(reddit)
            reddit_crawler.crawl(subreddit, date_from, date_to, min_length_comments, min_length_posts, blacklist_posts, blacklist_comments)

            collection_name = f'{subreddit}_{date_from}_{date_to}'
            crawled_documents = reddit_crawler.get_documents(collection_name)

            database_client.insert(collection_name, crawled_documents)

    except KeyError as error:
        app.logger.error('Error: KeyError: ' + str(error))

    return '200'