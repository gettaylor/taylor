import os
import logging
from uuid import uuid4
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
# Gets client ID from your environment variables
client_id = os.environ["SLACK_CLIENT_ID"]
# Gets client Secret from your environment variables
client_secret = os.environ["SLACK_CLIENT_SECRET"]
# Generates random string to use as state to stop CRSF attacks
state = str(uuid4())

# Scopes this this app
# oauth_scope = ", ".join(["channels:read", "groups:read", "channels:manage", "chat:write"])
oauth_scope = ", ".join(["channels:history", "chat:write", "groups:history", "groups:write", "im:history", "incoming-webhook", "mpim:history", "mpim:write", "users:read", "im:write"])

# Create a dict to represent a database to store token
# Currently used in the "/finish_auth" route
token_database = {}
global_token = ""

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

# Routing:
# Starts OAuth process
@app.route("/begin_auth", methods=["GET"])
def pre_install():
    return f'<a href="https://slack.com/oauth/v2/authorize?scope={ oauth_scope }&user_scope=channels:read&client_id={ client_id }&state={ state }"><img alt=""Add to Slack"" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a>'

# Route for OAuth flow to redirect to after user accepts scopes
@app.route("/finish_auth", methods=["GET", "POST"])
def post_install():
    # Gets the auth code and state from the request params
    auth_code = request.args["code"]
    received_state = request.args["state"]

    # Empty string is a valid token request
    client = WebClient(token="")

    # Verifies state received in param from received_state are the same
    if received_state == state:
        # Request the auth tokens from Slack
        response = client.oauth_v2_access(client_id=client_id, client_secret=client_secret, code=auth_code)
    else:
        return "Invalid State"
    
    # Save the bot token and teamID to the dict (CHANGE TO A DATABASE!!!)
    teamID = response["team"]["id"]
    token_database[teamID] = response["access_token"]

    # Saving the bot token in a global variable to save on looking up on WebClient calls
    global global_token
    # Saving bot token and team_id in the to an environments variable 
    global_token = response["access_token"]

    return "Auth Complete"

if __name__ == "__main__":
    logger = logging.getLogger()
    # logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.run(debug=True, port=3000)
