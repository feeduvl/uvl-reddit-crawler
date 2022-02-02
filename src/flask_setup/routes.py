from flask import Flask, request, json, jsonify
from src.api.utils import database_handler
from src.flask_setup import app
from src.api.request_handler import RequestHandler
import praw
import os

@app.route('/hitec/reddit/crawl', methods=['POST'])
def run_crawler():

    '''
    # Expected example request:

    request_content = {
        "subreddits":["ubuntu"],
        "collection_names":["ubuntu_data"],
        "date_from":"24-01-2022",
        "date_to":"28-01-2022",
        "min_length_posts":"20",
        "min_length_comments":"10",
        "comment_depth" : "1", # [0,1,2,3,4,5,"all"]
        "blacklist_comments":["foo"],
        "blacklist_posts":["bar"],
        "replace_urls" : "false",
        "replace_emojis" : "false"
    }
    '''
    if request.method == 'POST':
        request_content = request.get_json(force=True)
        app.logger.debug(str(request_content))


        reddit = praw.Reddit(
            client_id=os.environ["CLIENT_ID"],
            client_secret=os.environ["CLIENT_SECRET"],
            user_agent=os.environ["USER_AGENT"],
        )
        database_client = database_handler()

        client = RequestHandler(request_content,database_client,reddit,app.logger)
        client.run()

    else:
        app.logger.error('Error: Only POST implemented')
        return

    return '200'