import socket
import threading
import sched
import time
import requests
import json
import datetime

from config import *

data = {}


def get_data_from_line(line: str, channels_list: list) -> (str, str):
    username, channel = None, None
    is_sub, is_mod = False, False

    line_list = line.split(";")
    for e in line_list:
        if "display-name" in e:
            username = e.split("=")[1]
        elif "subscriber=" in e:
            is_sub = e.split("=")[1] == "1"
        elif "mod=" in e:
            is_mod = e.split("=")[1] == "1"
    
    # get the channel name, take the word after "PRIVMSG #" and before " :
    channel = line.split("PRIVMSG #")[1].split(" :")[0]
    # check if the channel is in the list of channels to listen
    if channel not in channels_list:
        print(f"\t\t {channel} not in channels_list")
        print("\t\t\n\n" , line, "\n\n")
        return None, None

    return channel, username, is_sub, is_mod


def remove_known_bots():
    global data
    # remove known bots
    for channel in data.keys():
        for bot in KNOWN_BOTS:
            if bot in data[channel]:
                data[channel].remove(bot)


class ListenChatThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""
    global data

    def __init__(self, channel:str, channels_info:list):
        super(ListenChatThread, self).__init__()
        self._stop_event = threading.Event()
        self._listen_ready = threading.Event()
        self.channel = channel
        self.channels_list = channels_info
        self.socket_irc = None

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def set_ready(self):
        self._listen_ready.set()

    def is_ready(self):
        return self._listen_ready.is_set()

    def connect(self):
        # print(f"\t\t CONNECTING TO {self.channel}")
        irc = socket.socket()
        irc.connect((SERVER, 6667)) #connects to the server

        #sends variables for connection to twitch chat
        irc.send(('PASS ' + PASSWORD + '\r\n').encode())
        irc.send(('USER ' + NICK + ' 0 * :' + BOT_OWNER + '\r\n').encode())
        irc.send(('NICK ' + NICK + '\r\n').encode())

        irc.send(('CAP REQ :twitch.tv/tags\r\n').encode())
        irc.send(('CAP REQ :twitch.tv/commands\r\n').encode())
        irc.send(('raw CAP REQ :twitch.tv/membership\r\n').encode())

        irc.send(('JOIN #' + self.channel + '\r\n').encode())

        return irc
    
    def start_listen(self):
        # print(f"\t\t START LISTENING {self.channel}")

        readbuffer=""
        while not self.stopped():
            try:
                readbuffer = readbuffer + self.socket_irc.recv(1024).decode() 
            except socket.timeout:
                pass
            except UnicodeDecodeError:
                pass

            taco = readbuffer.split("\n")
            readbuffer = taco.pop()
            for line in taco:
                if("PRIVMSG" in line):
                    c, username, is_sub, is_mod = get_data_from_line(line, self.channels_list)

                    if c is None or username is None:
                        continue

                    if username in KNOWN_BOTS:
                        continue

                    if data[self.channel]["chatters"].get(username) is None:
                        data[self.channel]["chatters"][username] = {"is_sub": is_sub, "is_mod": is_mod, "count_messages": 1}
                    else:
                        data[self.channel]["chatters"][username]["count_messages"] += 1

                elif("PING" in line):
                    self.socket_irc.send(("PONG %s\r\n" % line[1]).encode())
        
        self.socket_irc.close()
        return

    def run(self):
        irc = self.connect()
        readbuffer = irc.recv(1024).decode()
        count = 0
        while "Login unsuccessful" in readbuffer and count < 5:
            irc.close()
            time.sleep(0.3)
            irc = self.connect()
            readbuffer = irc.recv(1024).decode()
            count += 1

        if count >= 5:
            print(f"\t\t LOGIN UNSUCCESSFUL FOR {self.channel}")
            return

        self.socket_irc = irc
        self.socket_irc.settimeout(4)

        while self.is_ready() is False:
            # throw away the messages until the thread is ready
            try:
                self.socket_irc.recv(1024).decode()
            except socket.timeout:
                pass
            time.sleep(0.1)
        
        self.start_listen()


def kill_threads(thread_list: list):
    # kill all the threads
    for i, t in enumerate(thread_list):
        t.stop()

    # wait for all the threads to finish
    for i, t in enumerate(thread_list):
        t.join()
        # print(f"\t\t THREAD {i+1} / {len(thread_list)} KILLED")


def save_and_restart(scheduler, thread_list: list):
    global data

    print("\t\t KILLING THREADS")
    kill_threads(thread_list)

    # get the new channels info
    channels_info = get_channels_info()

    # adjust the viewer count with the average of the previous and the new one
    for channel in channels_info.keys():
        if channel not in data.keys():
            continue
        else:
            data[channel]["viewer_count"] = int((data[channel]["viewer_count"] + channels_info[channel]["viewer_count"]) / 2)

    # save the data
    filename = f"dumps/{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.json"
    print(f"\t\t SAVING CHATTERS IN {filename}")
    
    remove_known_bots() # remove known bots
    
    with open(filename, "w") as f_w:
        json.dump(data, f_w, indent=4)

    # restart the threads
    print("\t\t RESTARTING THREADS")
    thread_list = launch_threads(channels_info)

    scheduler.enter(RESTART_TIME, 1, save_and_restart, (scheduler, thread_list))    # schedule the next saving


def launch_threads(channels_info = None) -> list:
    thread_list = []

    if channels_info is None:   # if the channels info are not passed as argument, get them
        channels_info = get_channels_info()
    initialize_data(channels_info)

    # launch one thread for each channel
    print("\t\t LAUNCHING THREADS")
    for channel in channels_info.keys():
        t = ListenChatThread(channel, channels_info.keys())
        t.start()
        thread_list.append(t)
        time.sleep(0.5)     # wait to avoid the unsuccessful login error (probably for too many requests)

    # now that all the threads are launched, set the ready flag to start listening to the chat
    for t in thread_list:
        t.set_ready()
    
    print("\t\t THREADS LAUNCHED")

    return thread_list


def get_channels_info() -> list:
    #make a request to the twitch api to get the list of channels
    url = f"https://api.twitch.tv/helix/streams?language=it&first={N_STREAMS}"
    headers = {
        "Authorization": AUTHORIZATION_TWITCH_API,
        "Client-Id": CLIENT_ID
    }

    response = requests.get(url, headers=headers)

    streamers_info = {}
    for i in range(len(response.json()["data"])):
        username_streamer = response.json()["data"][i]["user_name"].lower()
        streamers_info[ username_streamer ] = {}
        streamers_info[ username_streamer ]["game_name"] = response.json()["data"][i]["game_name"]
        streamers_info[ username_streamer ]["viewer_count"] = response.json()["data"][i]["viewer_count"]

    return streamers_info


def initialize_data(channels_info):
    global data

    data = {}
    for streamer in channels_info.keys():
        data[streamer] = {}
        data[streamer]["game_name"] = channels_info[streamer]["game_name"]
        data[streamer]["viewer_count"] = channels_info[streamer]["viewer_count"]
        data[streamer]["chatters"] = {}


def main():
    thread_list = launch_threads()

    # launch a scheduler to save the data and restart the threads
    my_scheduler = sched.scheduler(time.time, time.sleep)
    my_scheduler.enter(RESTART_TIME, 1, save_and_restart, (my_scheduler, thread_list))
    my_scheduler.run()


if __name__ == "__main__":
    main()
