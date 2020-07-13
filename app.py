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
    message_for_white_list = event_data["event"]
    message_for_black_list = event_data["event"]
    message_for_master = event_data["event"]
    message_for_slave = event_data["event"]
    message_for_guys = event_data["event"]
    user = event_data["event"]["user"]
    
    if "white list" in message_for_white_list.get('text').lower() or "white-list" in message_for_white_list.get('text').lower() or "whitelist" in message_for_white_list.get('text').lower():
        message_for_white_list = f"Hi <@%s>, instead of using {message_for_white_list.get('text')}, please use Allow List as a preferred inclusive word." % message_for_white_list["user"]
        response = client.conversations_open(users=[user])
        response = client.chat_postMessage(channel=response.get("channel")["id"], text=message_for_white_list)
    
    if "black list" in message_for_black_list.get('text').lower() or "black-list" in message_for_black_list.get('text').lower() or "blacklist" in message_for_black_list.get('text').lower():
        message_for_black_list = f"Hi <@%s>, please use Deny List instead of {message_for_black_list.get('text')} as a preferred inclusive word." % message_for_white_list["user"]
        response = client.conversations_open(users=[user])
        response = client.chat_postMessage(channel=response.get("channel")["id"], text=message_for_black_list)
    
    if "master" in message_for_master.get('text').lower():
        message_for_master = f"Hi <@%s>, please use Primary instead of {message_for_master.get('text')} as a preferred inclusive word." % message_for_master["user"]
        response = client.conversations_open(users=[user])
        response = client.chat_postMessage(channel=response.get("channel")["id"], text=message_for_master)

    if "slave" in message_for_slave.get('text').lower():
        message_for_slave = f"Hi <@%s>, please use Secondary instead of {message_for_slave.get('text')} as a preferred inclusive word." % message_for_slave["user"]
        response = client.conversations_open(users=[user])
        response = client.chat_postMessage(channel=response.get("channel")["id"], text=message_for_slave)

    if "guys" in message_for_guys.get('text').lower():
        message_for_guys = f"Hi <@%s>, please use peeps, people, y'all, folks or any other non gendered pronoun instead of {message_for_guys.get('text')} to promote inclusion." % message_for_guys["user"]
        response = client.conversations_open(users=[user])
        response = client.chat_postMessage(channel=response.get("channel")["id"], text=message_for_guys)  

if __name__ == "__main__":
    logger = logging.getLogger()
    # logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.run(debug=True, port=3000)
