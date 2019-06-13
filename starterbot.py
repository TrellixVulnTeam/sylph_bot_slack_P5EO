import os
import time
import re
from slackclient import SlackClient
from bot_key import bot_key

#instantiate the Slack client
slack_client = SlackClient(bot_key)
#sylph_bot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

#constants
RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


def parse_bot_commands(slack_events):
    # Parses list of events coming from Slack RTM API to find bot commands.
    # If a bot command is found, returns tuple of command and channel.
    # If its not found, then this function returns None, None.

    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None


def parse_direct_mention(message_text):
    # Finds direct mention in message text and returns the user ID which was mentioned.
    # If there is no direct mention, returns None
    matches = re.search(MENTION_REGEX, message_text)
    # first group contains username, second group contains remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(command, channel):
    # Executes bot command if the command is known
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None

    # This is where you start to implement more commands
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then"

    # Sends response back to channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("SYLPH Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")