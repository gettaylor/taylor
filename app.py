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

# trigger_words = ["white list", "white-list", "whitelist", "black list", "blacklist", "master", "guys"]

# Scopes: 
# Create an event listener for messaging events
# Sends a DM to the user who uses improper inclusion words
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    user_id = event_data["event"]["user"]

    trigger_words = ["white list", "white-list", "whitelist", "black list", "blacklist", "black-list", "master", "guys"]

    ## look for the trigger words that were used
    found_trigger_words = set()
    for word in trigger_words:
        if word in message.get("text").lower(): 
            found_trigger_words.add(word)

    if len(found_trigger_words) == 0:
        print("message contained 0 trigger words")
        return

    ## if there is exactly 1, take a shortcut and send
    if len(found_trigger_words) == 1:
        print("message contained exactly 1 trigger word")
        direct_message = f"Hi <@{message['user']}>, you used the non-inclusive word \"{list(found_trigger_words)[0]}\" in your recent message"
        response = client.conversations_open(users=[user_id])
        response = client.chat_postMessage(channel=response.get("channel")["id"], text=direct_message)
        return
    
    ## multiple trigger words
    print("message contained %d trigger words" % len(found_trigger_words))
    direct_message = f"Hi <@{message['user']}>, you used the following {len(found_trigger_words)} non-inclusive words in your recent message: {', '.join(list(found_trigger_words))}"
    response = client.conversations_open(users=[user_id])
    response = client.chat_postMessage(channel=response.get("channel")["id"], text=direct_message)
    
if __name__ == "__main__":
    logger = logging.getLogger()
    # logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.run(debug=True, port=3000)
