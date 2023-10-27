import socket
import threading
import sched
import time
import requests
import json
import datetime

from config import *

data = {}
stop_threads = False    # used to stop the threads, set to True when the scheduler calls save_and_restart()


def get_data_from_line(line: str, channels_list: list) -> (str, str):
    line_list = line.split(";")
    for e in line_list:
        if "display-name" in e:
            username = e.split("=")[1]
    
    # get channel name
    channel = line.split("#")[-1].split(" ")[0]
    if channel not in channels_list:
        print(f"\t\t {channel} not in channels_list")
        print(line)
        return None, None

    return channel, username


def listen_chat(channel: str, channels_list: list):
    global data, stop_threads

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
    while not stop_threads:
        readbuffer = readbuffer+irc.recv(1024).decode()
        taco = readbuffer.split("\n")
        readbuffer = taco.pop()
        for line in taco:
            if("PRIVMSG" in line):
                channel, username = get_data_from_line(line, channels_list)

                if channel is None or username is None:
                    continue
                
                #save the channel and username
                if channel not in data.keys():
                    data[channel] = []
                if username not in data[channel]:
                    data[channel].append(username)

            elif("PING" in line):
                irc.send(("PONG %s\r\n" % line[1]).encode())
                print(f"\t\tPONG {channel}")
    
    irc.close()
    return


def save_and_restart(scheduler, thread_list: list):
    global data, stop_threads

    # kill all the threads
    print("\t\t KILLING THREADS (it may take a while)")
    stop_threads = True
    for t in thread_list:
        t.join()
    stop_threads = False

    # save the data
    filename = f"dumps/{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.json"
    print(f"\t\t SAVING CHATTERS IN {filename}")
    with open(filename, "w") as f_w:
        json.dump(data, f_w, indent=4)

    data = {}   # clear the data

    # restart the threads
    print("\t\t RESTARTING THREADS")
    thread_list = launch_threads()

    scheduler.enter(RESTART_TIME, 1, save_and_restart, (scheduler, thread_list))    # schedule the next saving


def get_channels() -> list:
    #make a request to the twitch api to get the list of channels
    url = f"https://api.twitch.tv/helix/streams?language=it&first={N_STREAMS}"
    headers = {
        "Authorization": AUTHORIZATION_TWITCH_API,
        "Client-Id": CLIENT_ID
    }

    response = requests.get(url, headers=headers)
    streamers = [x["user_name"].lower() for x in response.json()["data"]]   # save in lowercase because irc channel names are lowercase

    print("\t\t chats to listen: ", streamers)
    return streamers


def launch_threads() -> list:
    thread_list = []

    channels_list = get_channels()

    # launch one thread for each channel
    for channel in channels_list:
        t = threading.Thread(target=listen_chat, args=(channel, channels_list))
        t.start()
        thread_list.append(t)
        time.sleep(0.5)     # wait to avoid the unsuccessful login error (probably for too many requests)

    return thread_list


def main():
    thread_list = launch_threads()

    # launch a scheduler to +++AAAAAAAAAAAAAAA+++
    my_scheduler = sched.scheduler(time.time, time.sleep)
    my_scheduler.enter(RESTART_TIME, 1, save_and_restart, (my_scheduler, thread_list))
    my_scheduler.run()


if __name__ == "__main__":
    main()
