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
client = WebClient(token=os.environ["SLACK_API_TOKEN"])


@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    user = event_data["event"]["user"]
   
    if "whitelist" in message.get('text').lower():
        message = "Hi <@%s>! Please use Allow List and NOT white list" % message["user"]
        response = client.conversations_open(users=[user])
        response = client.chat_postMessage(channel=response.get("channel")["id"], text=message)
        

if __name__ == "__main__":
    logger = logging.getLogger()
    # logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.run(debug=True, port=3000)
