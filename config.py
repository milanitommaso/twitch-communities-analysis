import json

BOT_OWNER = 'milanitommaso'
NICK = 'milanitommaso'
SERVER = 'irc.twitch.tv'

# take the credentials from the json file
with open('credentials.json') as json_file:
    data = json.load(json_file)
    PASSWORD = data['password_irc']
    AUTHORIZATION_TWITCH_API = data['authorization_twitch_api']
    CLIENT_ID = data['client_id']

SAVING_TIME = 600   #10 minutes
