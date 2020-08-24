import os, logging
import random
from uuid import uuid4
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from flask import Flask, request, _app_ctx_stack, jsonify, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

# Initialize a Flask app to host the events adapter and start the DB session
taylor_app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(
    os.environ["SLACK_SIGNING_SECRET"], "/slack/events", taylor_app
)

if "DATABASE_URL" in os.environ:
    taylor_app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
else:
    taylor_app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///./slack_test.db"

## Creating the DB
db = SQLAlchemy(taylor_app)

## Creating the table
class TeamInstall(db.Model):
    __tablename__ = "team_install"

    id = db.Column(db.Integer, primary_key=True)
    bot_access_token = db.Column(db.String)
    team_name = db.Column(db.String)
    team_id = db.Column(db.String)

    def __init__(self, bot_access_token=None, team_name=None, team_id=None):
        self.bot_access_token = bot_access_token
        self.team_name = team_name
        self.team_id = team_id

    def __repr__(self):
        return "<Team(bot_access_token='%s', team_name='%s', team_id='%s')>" % (self.bot_access_token, self.team_name, self.team_id)
        

# Gets client ID from your environment variables
client_id = os.environ["SLACK_CLIENT_ID"]
# Gets client Secret from your environment variables
client_secret = os.environ["SLACK_CLIENT_SECRET"]
# Generates random string to use as state to stop CRSF attacks
state = str(uuid4())

# Scopes this app needs to work
oauth_scope = ", ".join(["channels:history", "chat:write", "groups:history", "groups:write", "im:history", "incoming-webhook", "mpim:history", "mpim:write", "users:read", "im:write"])


# Create an event listener for messaging events
# Sends a DM to the user who uses improper inclusion words
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    user_id = event_data["event"]["user"]
    
    ## Created proper verbiage dictionary
    proper_verbiage = {
        "white list": "allow list", 
        "whitelist": "allow list", 
        "white-list": "allow list", 
        "black list": "deny list", 
        "blacklist": "deny list", 
        "black-list": "deny list", 
        "master": "primary", 
        "guys": random.choice(["everyone", "folks", "y'all", "peeps"])
       
    }

    trigger_words = ["white list", "white-list", "whitelist", "black list", "blacklist", "black-list", "master", "guys"]
    
    ## look for the trigger words that were used
    found_trigger_words = set()
    for word in trigger_words:
        if word in message.get("text").lower(): 
            found_trigger_words.add(word)

    if len(found_trigger_words) == 0:
        print("message contained 0 trigger words")
        return

    team_install = TeamInstall.query.filter_by(team_id=event_data["team_id"]).first()
    client = WebClient(token=team_install.bot_access_token)
    
    ## Checks to see if the user is_restricted or ultra_restricted to be able to send DM to only them
    response_user = client.users_info(user=event_data["event"]["user"])
    if response_user.get("user")["is_restricted"]:
        return
    if response_user.get("user")["is_ultra_restricted"]:
        return

    ## if there is exactly 1, take a shortcut and send
    if len(found_trigger_words) == 1:
        print("message contained exactly 1 trigger word")

        direct_message = f"Hi <@{message['user']}>, you used the non-inclusive word \"{list(found_trigger_words)[0]}\" in your recent message, consider using \"{proper_verbiage[list(found_trigger_words)[0]]}\""
    
        response = client.conversations_open(users=[user_id])
        response = client.chat_postMessage(channel=response.get("channel")["id"], text=direct_message)
        
        return
        
    ## multiple trigger words
    print("message contained %d trigger words" % len(found_trigger_words))

    ## DM's user their message with a more inclusive message
    direct_message = message.get("text")
    for trigger_word in trigger_words:
        direct_message = direct_message.replace(trigger_word, f"~{trigger_word}~ *{proper_verbiage[trigger_word]}*")
    direct_message = f"Hi <@{message['user']}>, you used {len(found_trigger_words)} non inclusive words in your recent message. Consider using the following message instead: \n\n {direct_message}"
    
    response = client.conversations_open(users=[user_id])
    response = client.chat_postMessage(channel=response.get("channel")["id"], text=direct_message)
    

## Uninstalling the app
@slack_events_adapter.on("app_uninstalled")
def uninstall_event(event_data):
    team_id = event_data["team_id"]

    ## Deletes Team from the database
    TeamInstall.query.filter_by(team_id=team_id).delete()
    db.session.commit()

# Routing:
# Starts OAuth process
@taylor_app.route("/begin_auth", methods=["GET"])
def pre_install():
    return f'<a href="https://slack.com/oauth/v2/authorize?scope={ oauth_scope }&user_scope=channels:read&client_id={ client_id }&state={ state }"><img alt=""Add to Slack"" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a>'

# Route for OAuth flow to redirect to after user accepts scopes
@taylor_app.route("/finish_auth", methods=["GET", "POST"])
def post_install():
    # Gets the auth code and state from the request params
    auth_code = request.args["code"]

    received_state = request.args["state"]

    # Empty string is a valid token request
    client = WebClient(token="")
   
    # Request the auth tokens from Slack
    response = client.oauth_v2_access(client_id=client_id, client_secret=client_secret, code=auth_code)
    
    teamID = response["team"]["id"]
    teamName = response["team"]["name"]

    botUserID = response["bot_user_id"]
    accessToken = response["access_token"]
    
    # Saving the bot token, team name and team id in the db
    team_install = TeamInstall(accessToken, teamName, teamID)
    db.session.add(team_install)
    db.session.commit()
    return redirect("https://gettaylor.app/gettingStarted.html", code=302)

if __name__ == "__main__":
    logger = logging.getLogger()
    # logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    taylor_app.run(debug=True, port=3000)
