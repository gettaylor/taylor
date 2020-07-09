import os
import logging
from slack import WebClient
from flask import Flask, request
from slackeventsapi import SlackEventAdapter

# Initialize a Flask app to host the events adapter
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(
    os.environ["SLACK_SIGNING_SECRET"], "/slack/events", app
)

# Initialize a Web API client
# slack_web_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

client = WebClient(token=os.environ["SLACK_API_TOKEN"])
res = client.api_test()



if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.run(port=3000)
