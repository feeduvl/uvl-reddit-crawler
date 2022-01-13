from flask import Flask, request, json, jsonify
#from src.api.crawler import RedditCrawler, DBMock
import praw

app = Flask(__name__)


@app.route('/')
def hello_world():
    print("console?")
    return "<p>Hello, World!</p>"


#@app.route('/run')
def run_crawler():
    #request_content = json.loads(request.data.decode('utf-8')) 
    request_content = {
        "subreddits" : ["ubuntu", "spotify"],
        "from_date" : "13112021",
        "to_date" : "28112021",
        "min_length_comments" : "",
        "min_length_posts" : "",
        "blacklist_comments" : [],
        "blacklist_posts" : [],
        

    }
    

    reddit = praw.Reddit(
        client_id="P0eMVNdwpy29g3K2LhCPTw",
        client_secret="9s-TrT5HJASoawBN951QWsUQTck-mg",
        user_agent="script:api_test:v1.0.0 (by u/uvl_reddit_crawler)",
    )

    database_client = DBMock()

    reddit_crawler = RedditCrawler(reddit, database_client)

    try:
        subreddits = request_content["subreddits"]
        from_date  = request_content["from_date"]
        to_date    = request_content["to_date"]

        blacklist_post    = request_content["blacklist_posts"]
        blacklist_comment = request_content["blacklist_comments"]

        min_length_post    = request_content["min_length_post"]
        min_length_comments = request_content["min_length_comments"]
        
        for subreddit in subreddits:

            reddit_crawler.crawl(subreddit, from_date, to_date)
    
    
    
    except KeyError as error:
        pass

    pass