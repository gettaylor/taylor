class MessagesTab:
    '''
    Creates the block of text that will DM users after they go to the messages tab
    '''
    MESSAGE_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Hi <@{message['user_id']}> :wave:, I'm Taylor and thank you for installing me!! I'm just a simple app that will only communicate full Slack members only if I'm told to do so. 
            "What does that mean? I only use DM's when a full member uses some non-inclusive terms. Other than that, I just hang out."
        }
    }
    
    def __init__(self, channel):
        self.channel = channel
        self.username = "Taylor"
        self.timestamp = ""
    
    def get_message_payload(self):
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": self.username,
            "blocks": [
                self.MESSAGE_BLOCK
            ]
        }