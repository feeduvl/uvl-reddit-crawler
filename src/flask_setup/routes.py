from flask import Flask, request, json, jsonify
from src.api.crawler import RedditCrawler, DBMock
from src.flask_setup import app
import praw

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
        data = request.get_json(force=True)
        return data
    else:
        return 'not post'
    
    return request_content

    
    # MISSING: Credentials
    reddit = praw.Reddit(
        client_id="",
        client_secret="",
        user_agent="",
    )

    database_client = DBMock()

    reddit_crawler = RedditCrawler(reddit, database_client)

    try:
        subreddits = request_content["subreddits"]
        from_date  = request_content["from_date"]
        to_date    = request_content["to_date"]

        min_length_comments = request_content["min_length_comments"]
        min_length_posts = request_content["min_length_posts"]

        blacklist_posts    = request_content["blacklist_posts"]
        blacklist_comments = request_content["blacklist_comments"]
        
        for subreddit in subreddits:

            reddit_crawler.crawl(subreddit, from_date, to_date, min_length_comments, min_length_posts, blacklist_posts, blacklist_comments)
    
    # MISSING: Purposeful DB insert
    except KeyError as error:
        return f'<p> Error: {repr(error)} </p>'

    return "<p> Success? </p>"