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
res = client.api_test()

# Storing the SlackClient instances for each team in a
# dictionary, so we can have multiple teams authed
CLIENTS = {}

# def listening(user_id: str, channel: str):
    
#     # Get the onboarding message payload
#     message = onboarding_tutorial.get_message_payload()

#     # Post the onboarding message in Slack
#     response = slack_web_client.chat_postMessage(**message)

#     # Capture the timestamp of the message we've just posted so
#     # we can use it to update the message after a user
#     # has completed an onboarding task.
#     onboarding_tutorial.timestamp = response["ts"]

#     # Store the message sent in onboarding_tutorials_sent
#     if channel not in onboarding_tutorials_sent:
#         onboarding_tutorials_sent[channel] = {}
#     onboarding_tutorials_sent[channel][user_id] = onboarding_tutorial

# ============== Message Events ============= #
# When a user sends a DM, the event type will be 'message'.
# Here we'll link the message callback to the 'message' event.
# @slack_events_adapter.on("message")
# def message(payload):
#     """Display the onboarding welcome message after receiving a message
#     that contains "start".
#     """
#     event = payload.get("event", {})

#     channel_id = event.get("channel")
#     user_id = event.get("user")
#     text = event.get("text")
#     print(text)

#     if text and text.lower() == "whitelist":
#         return start_onboarding(user_id, channel_id)

# Now we'll set up some event listeners for our app to process and respond to
# Example responder to greetings

# Prints in the channel the message on line 66
# TODO make it stop repeating the message from me and Taylor
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    if message.get("subtype") is None and "whitelist" in message.get('text'):
        channel = message["channel"]
        message = "Hi <@%s>! Please use Allow List and NOT that word" % message["user"]
        client.chat_postMessage(channel=channel, text=message)

        # print(message('text'))

# @slack_events_adapter.on("message")
# def handle_message(event_data):
#     # channel = event_data["event"]
#     # user = event_data["event"]
#     message = event_data["event"]

#     print(message)
#     # print(message.get('text'))
#     if message.get("subtype") is None and "whitelist" in message.get('text'):
#     # if message.get('text').lower() == "whitelist":
#         # channel = message["user"]
#         channel = message["channel"]
#         message = "Hi <@%s>! :tada:" % message["user"]
#         # message = "Please use Allow List instead of Whitelist" % message["user"]
#         # client.send(message['user'], 'you said the wrong word')
#         client.api_call("chat.postMessage", channel=channel, text=message) #user=user,
#         # client[user].api_call("chat.postMessage", text=message, channel=channel) #user=user,

#         # print(message.get('text'))
#     # if message.get("subtype") is None and "whitelist" in message.get('text'):
#     #     user = message["user"]
#     #     message = "Please use Allow List instead of Whitelist" % message["user"]
#     #     client[user].api_call("chat.postMessage", user=user, text=message)
        
#         # print(message.get('text'))
       


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.run(debug=True, port=3000)
