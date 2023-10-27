import json

BOT_OWNER = 'milanitommaso'
NICK = 'milanitommaso'
SERVER = 'irc.twitch.tv'
N_STREAMS = 100
RESTART_TIME = 600   #10 minutes

# take the credentials from the json file
try:
    with open('credentials.json') as json_file:
        data = json.load(json_file)
        PASSWORD = data['password_irc']
        AUTHORIZATION_TWITCH_API = data['authorization_twitch_api']
        CLIENT_ID = data['client_id']
except FileNotFoundError:
    print("credentials.json not found, please create it")
    exit(1)

