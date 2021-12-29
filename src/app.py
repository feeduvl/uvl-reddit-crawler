from flask import Flask, request, json, jsonify


app = Flask(__name__)


@app.route('/', methods["POST"])
def run_crawler:
    request_content = json.loads(request.data.decode('utf-8')) 
    reddit_crawler = RedditCrawler()

    try:
        subreddits = request_content[""]
        from_date  = request_content[""]
        to_date    = request_content[""]

        blacklist_post    = request_content[""]
        blacklist_comment = request_content[""]

        min_length_post    = request_content[""]
        min_length_comment = request_content[""]
        
        for subreddit in subreddits:

            reddit_crawler.crawl()
    except KeyError as error:
        pass

    pass