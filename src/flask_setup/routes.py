"""This module contains the REST entry point and manages
the calls the actual reddit API.
"""
import os
import praw

from flask import request

from src.api.utils import DatabaseHandler
from src.flask_setup import app
from src.api.request_handler import RequestHandler

@app.route('/hitec/reddit/crawl', methods=['POST'])
def run_crawler():
    """ This function handles the flask routing to the crawler API.

    It is only possible to make POST request to this function. The function
    expects an client ID, client secret and user agent in the environment
    variables for the praw reddit API. The HTTP request must have this
    structure:

    Expected example request:

    request_content = {
        "subreddits":["ubuntu"],
        "collection_names":["ubuntu_data"],
        "date_from":"24-01-2022",
        "date_to":"28-01-2022",
        "min_length_posts":"20",
        "min_length_comments":"10",
        "comment_depth" : "1", # [0,1,2,3,4,5,6 which means all]
        "blacklist_comments":["foo"],
        "blacklist_posts":["bar"],
        "replace_urls" : "false",
        "replace_emojis" : "true"
    }
    """
    if request.method == 'POST':
        request_content = request.get_json(force=True)
        app.logger.info(str(request_content))

        try:
            reddit = praw.Reddit(
                client_id=os.environ["CLIENT_ID"],
                client_secret=os.environ["CLIENT_SECRET"],
                user_agent=os.environ["USER_AGENT"],
            )
        except KeyError as error:
            app.logger.error(str(error))
            return 'ERROR'

        database_client = DatabaseHandler()

        try:
            client = RequestHandler(request_content,database_client,reddit,app.logger)
            client.run()
        except KeyError as error:
            app.logger.error(str(error))
            return 'ERROR'


    else:
        app.logger.error('Error: Only POST implemented')
        return 'ERROR'

    return 'OK'
