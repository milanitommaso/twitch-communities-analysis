import json

BOT_OWNER = 'milanitommaso'
NICK = 'milanitommaso'
SERVER = 'irc.twitch.tv'
N_STREAMS = 200
CHECK_CHANNELS_TIME = 600
KEEP_CHANNEL_COUNT = 3
RELOAD_IRC_CONNECTION_TIME = 10800    # 3 hours
KNOWN_BOTS = ['Nightbot', 'StreamElements', 'Streamlabs', 'Moobot', "Fossabot", "SonglistBot", "Wizebot"]
ALLOWED_USERNOTICE = ['sub', 'resub', 'subgift', 'submysterygift', 'giftpaidupgrade', 'rewardgift', 'anongiftpaidupgrade', 'raid']

# take the credentials from the json file
try:
    with open('data_downloader/credentials.json') as json_file:
        data = json.load(json_file)
        PASSWORD = data['password_irc']
        AUTHORIZATION_TWITCH_API = data['authorization_twitch_api']
        CLIENT_ID = data['client_id']
except FileNotFoundError:
    print("credentials.json not found, please create it")
    exit(1)
