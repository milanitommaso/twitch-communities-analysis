import socket
import threading
import sched
import time
import requests
import json
import datetime

from config import *

data = {}

def save_chatters(scheduler,):
    global data

    filename = f"dumps/{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.json"
    print(f"\t\t SAVING CHATTERS IN {filename}")
    with open(filename, "w") as f_w:
        json.dump(data, f_w, indent=4)

    print("\t\t CHATTERS SAVED")
    data = {}

    scheduler.enter(SAVING_TIME, 1, save_chatters, (scheduler,))    # schedule the next saving


def get_channels() -> list:
    #make a request to the twitch api to get the list of channels
    url = "https://api.twitch.tv/helix/streams?language=it"
    headers = {
        "Authorization": AUTHORIZATION_TWITCH_API,
        "Client-Id": CLIENT_ID
    }

    response = requests.get(url, headers=headers)
    streamers = [x["user_name"].lower() for x in response.json()["data"]]

    print(streamers)
    return streamers


def get_data_from_line(line: str):
    line_list = line.split(";")
    for e in line_list:
        if "display-name" in e:
            username = e.split("=")[1]
    
    # get channel name
    channel = line.split("#")[-1].split(" ")[0]
    if channel not in channels_list:
        print(f"\n\n\n-------------------- {channel}")
        print(line)
        print("-----------------------\n\n\n")
        return None, None

    return channel, username


def listen_chat(channel: str):
    irc = socket.socket()
    irc.connect((SERVER, 6667)) #connects to the server

    #sends variables for connection to twitch chat
    irc.send(('PASS ' + PASSWORD + '\r\n').encode())
    irc.send(('USER ' + NICK + ' 0 * :' + BOT_OWNER + '\r\n').encode())
    irc.send(('NICK ' + NICK + '\r\n').encode())

    irc.send(('CAP REQ :twitch.tv/tags\r\n').encode())
    irc.send(('CAP REQ :twitch.tv/commands\r\n').encode())
    irc.send(('raw CAP REQ :twitch.tv/membership\r\n').encode())

    irc.send(('JOIN #' + channel + '\r\n').encode())

    readbuffer=""
    while True:
        readbuffer = readbuffer+irc.recv(1024).decode()
        taco = readbuffer.split("\n")
        readbuffer = taco.pop()
        for line in taco:
            if("PRIVMSG" in line):
                channel, username = get_data_from_line(line)
                # print(channel, username)

                if channel is None or username is None:
                    continue
                
                #save the channel and username
                if channel not in data.keys():
                    data[channel] = []
                if username not in data[channel]:
                    data[channel].append(username)

            elif("PING" in line):
                irc.send(("PONG %s\r\n" % line[1]).encode())
                print("\n\n\n\n\n ------------------- \n\n\n\n\n\n\n")


def launch_threads(channels_list: list):
    # launch one thread for each channel
    for channel in channels_list:
        t = threading.Thread(target=listen_chat, args=(channel,))
        t.start()


channels_list = get_channels()

def main():
    t = threading.Thread(target=launch_threads, args=((channels_list,)))
    t.start()

    my_scheduler = sched.scheduler(time.time, time.sleep)
    my_scheduler.enter(SAVING_TIME, 1, save_chatters, (my_scheduler,))
    my_scheduler.run()


if __name__ == "__main__":
    main()
