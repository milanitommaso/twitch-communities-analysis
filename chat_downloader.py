import random
import socket
import threading
import sched
import time
import requests
import json
import datetime
import os

from config import *
from notify_telegram import notify_error as notify_error


def get_channels_to_listen() -> list:
    # take the list of channels from the last file in /stream_info folder
    channels_list = []

    filename = "streams_info/" + sorted(os.listdir("streams_info"))[-1]
    print(f"> Reading channels from {filename}")
    with open(filename, "r") as f:
        count = 0
        for line in f.readlines():
            count += 1
            channels_list.append(line.split("\t")[0])

            if count >= N_STREAMS:
                break

    return channels_list


def start_threads(channels_list: list) -> dict:
    # launch the threads to listen the chats
    print("> Start threads to listen chats")
    threads_dict = {}

    for channel in channels_list:
        t = ListenChatThread(channel, channels_list)
        threads_dict[channel] = t
        t.start()
        time.sleep(0.5) # wait to avoid login unsuccessful error for too many requests

    print("> Threads launched")

    return threads_dict


def check_channels(threads: dict):
    # before checking the channels save the chat logs
    save_chat_logs(threads)

    print("> Checking channels")
    # check if the channels are still in the list of channels to listen
    channels_list = get_channels_to_listen()
    for channel in channels_list:
        if channel not in threads.keys():
            # start a new thread
            t = ListenChatThread(channel, channels_list)
            threads[channel] = t
            t.start()
            time.sleep(0.5) # wait to avoid login unsuccessful error for too many requests
            print(f"> Thread started for channel {channel}")

    for channel in threads.keys():
        if channel not in channels_list:
            threads[channel].decrease_keep_channel_count()
            print(f"> Decrease keep channel count for channel {channel}")
        else:
            threads[channel].reset_keep_channel_count()

    # remove the threads that are no more in the list of channels to listen
    for channel in list(threads.keys()):
        if threads[channel].is_stopped():
            threads[channel].join()
            del threads[channel]
            print(f"> Thread stopped for channel {channel}")

    # decrease the ttl of the threads
    for channel in list(threads.keys()):
        error = threads[channel].decrease_ttl()
        if error == -1:
            threads[channel].join()
            del threads[channel]
            print(f"> Unsuccessful login for {channel}")
            notify_error(f"Unsuccessful login for {channel} during reload of the irc connection")

    # schedule the next check
    sched_check_channels = sched.scheduler(time.time, time.sleep)
    sched_check_channels.enter(CHECK_CHANNELS_TIME, 1, check_channels, (threads,))
    sched_check_channels.run()


def save_chat_logs(threads: dict):
    print("> Saving chat logs")
    for channel in threads.keys():
        threads[channel].save_chat_log()


def get_data_from_line(line: str, channels_list: list) -> (str, int, int, str, str):
    timestamp, is_sub, is_mod, username, message = None, None, None, None, None

    timestamp = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S")

    line_list = line.split(";")
    for e in line_list:
        if "display-name" in e:
            username = e.split("=")[1]
        elif "subscriber=" in e:
            is_sub = int(e.split("=")[1] == "1")
        elif "mod=" in e:
            is_mod = int(e.split("=")[1] == "1")
    
    # get the channel name, take the word after "PRIVMSG #" and before " :"
    try:
        channel = line.split("PRIVMSG #")[1].split(" :")[0]
    except:
        channel = None

    # check if the channel is in the list of channels to listen
    if channel is None or channel not in [x.lower() for x in channels_list]:
        print(f"\t\t CHANNEL {channel} NOT IN THE LIST OF CHANNELS TO LISTEN")
        return None, None, None, None, None

    # get the message
    try:
        message = "".join(line.split("PRIVMSG #")[1].split(" :")[1]).strip()
    except:
        message = None
    
    return timestamp, is_mod, is_sub, username, message


class ListenChatThread(threading.Thread):
    def __init__(self, channel:str, channels_info:list):
        super(ListenChatThread, self).__init__()
        self._stop_event = threading.Event()
        self.keep_channel_count = KEEP_CHANNEL_COUNT      # used to know when the channel is no more in the list of channels to listen
        self.channel = channel
        self.channels_list = channels_info
        self.socket_irc = None
        self.chat_log = ""
        self.log_filename = f"downloaded_chats/{channel}/chat_{datetime.datetime.now().strftime('%y-%m-%d_%H-%M-%S')}.txt"
        self._reloading_irc_connection = threading.Event()
        self.ttl = int(RELOAD_IRC_CONNECTION_TIME / CHECK_CHANNELS_TIME * random.uniform(0.6, 1.2)) # randomize the ttl to avoid all the threads to reload the connection at the same time

    def set_stop(self):
        self._stop_event.set()

    def is_stopped(self):
        return self._stop_event.is_set()

    def reset_keep_channel_count(self):
        self.keep_channel_count = KEEP_CHANNEL_COUNT

    def decrease_keep_channel_count(self):
        self.keep_channel_count -= 1

        if self.keep_channel_count <= 0:
            self.set_stop()

    def set_reloading_irc_connection(self):
        self._reloading_irc_connection.set()

    def clear_reloading_irc_connection(self):
        self._reloading_irc_connection.clear()

    def is_reloading_irc_connection(self):
        return self._reloading_irc_connection.is_set()

    def decrease_ttl(self):
        self.ttl -= 1

        if self.ttl <= 0:
            ret = self.reload_irc_connection()
            return ret
        
    def save_chat_log(self):
        # check if the folder exists
        if not os.path.exists(f"downloaded_chats/{self.channel}"):
            os.makedirs(f"downloaded_chats/{self.channel}")

        with open(self.log_filename, "a") as f:
            f.write(self.chat_log)
        self.chat_log = ""

    def reload_irc_connection(self):
        print(f"> Reloading irc connection for {self.channel}")
        self.set_reloading_irc_connection()     # set the flag to avoid the thread to listen the chat while reloading the connection

        time.sleep(5.5)   # wait that the thread pause the listening of the chat

        self.socket_irc.close()

        self.socket_irc = self.connect()    # set the new irc socket
        self.ttl = int(RELOAD_IRC_CONNECTION_TIME / CHECK_CHANNELS_TIME * random.uniform(0.6, 1.2)) # randomize the ttl to avoid all the threads to reload the connection at the same time

        readbuffer = self.socket_irc.recv(1024).decode()
        count = 0
        while "Login unsuccessful" in readbuffer and count < 15:
            self.socket_irc.close()
            time.sleep(random.uniform(0.5, 3))    # randomize the sleep to avoid all the threads to reload the connection at the same time
            self.socket_irc = self.connect()
            readbuffer = self.socket_irc.recv(1024).decode()
            count += 1

        if count >= 15:
            self.socket_irc.close()
            return -1
        
        self.socket_irc.settimeout(5)

        self.clear_reloading_irc_connection()   # clear the flag to allow the thread to listen the chat
        print(f"> Reloaded irc connection for {self.channel}")

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
        readbuffer = ""
        while not self.is_stopped():
            if self.is_reloading_irc_connection():  # wait for the connection to be ready, used for the reload of the irc connection
                time.sleep(0.)
                continue

            try:
                readbuffer = self.socket_irc.recv(1024).decode() 
            except socket.timeout:
                pass
            except UnicodeDecodeError:
                pass

            lines = readbuffer.split("\n")
            for line in lines:
                if "PRIVMSG" in line:
                    timestamp, is_mod, is_sub, username, message = get_data_from_line(line, self.channels_list)

                    if timestamp is None or is_mod is None or is_sub is None or username is None or message is None:
                        continue

                    self.chat_log += f"{timestamp}\t{is_mod}\t{is_sub}\t{username}\t{message}\n"

                elif "PING" in line:
                    self.socket_irc.send(("PONG :tmi.twitch.tv\r\n").encode())

            readbuffer = ""
        
        if self.is_stopped():
            self.socket_irc.close()
            return
    
    def run(self):
        self.socket_irc = self.connect()
        readbuffer = self.socket_irc.recv(1024).decode()
        count = 0
        while "Login unsuccessful" in readbuffer and count < 5:
            self.socket_irc.close()
            time.sleep(0.5)
            self.socket_irc = self.connect()
            readbuffer = self.socket_irc.recv(1024).decode()
            count += 1

        if count >= 5:
            print(f"> Login unsuccessful {self.channel}")
            self.socket_irc.close()
            return

        self.socket_irc.settimeout(5)
        
        self.start_listen()


def main():
    channels_list = get_channels_to_listen()
    threads = start_threads(channels_list)

    # schedule the re-check of the channels to listen
    sched_check_channels = sched.scheduler(time.time, time.sleep)
    sched_check_channels.enter(CHECK_CHANNELS_TIME, 1, check_channels, (threads,))
    sched_check_channels.run()


if __name__ == "__main__":
    main()
    # try:
    #     main()
    # except KeyboardInterrupt:
    #     pass
    # except Exception as e:
    #     notify_error(e)
    #     print("ERROR")
