import socket
import threading
import sched
import time
import requests
import json
import datetime

from config import *

data = {}
t_killer_thread = None  # used to kill all the threads when the scheduler calls save_and_restart()


def get_data_from_line(line: str, channels_list: list) -> (str, str):
    username, channel = None, None

    line_list = line.split(";")
    for e in line_list:
        if "display-name" in e:
            username = e.split("=")[1]
    
    # get the channel name, take the word after "PRIVMSG #" and before " :
    channel = line.split("PRIVMSG #")[1].split(" :")[0]
    # check if the channel is in the list of channels to listen
    if channel not in channels_list:
        print(f"\t\t {channel} not in channels_list")
        print("\t\t\n\n" , line, "\n\n")
        return None, None

    return channel, username


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

    def __init__(self, channel:str, channels_list:list):
        super(ListenChatThread, self).__init__()
        self._stop_event = threading.Event()
        self.channel = channel
        self.channels_list = channels_list

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
    
    def run(self):
        irc = socket.socket()
        irc.settimeout(10)
        irc.connect((SERVER, 6667)) #connects to the server

        #sends variables for connection to twitch chat
        irc.send(('PASS ' + PASSWORD + '\r\n').encode())
        irc.send(('USER ' + NICK + ' 0 * :' + BOT_OWNER + '\r\n').encode())
        irc.send(('NICK ' + NICK + '\r\n').encode())

        irc.send(('CAP REQ :twitch.tv/tags\r\n').encode())
        irc.send(('CAP REQ :twitch.tv/commands\r\n').encode())
        irc.send(('raw CAP REQ :twitch.tv/membership\r\n').encode())

        irc.send(('JOIN #' + self.channel + '\r\n').encode())

        readbuffer=""
        while not self.stopped():
            try:
                readbuffer = readbuffer+irc.recv(1024).decode() 
            except socket.timeout:
                pass
            except UnicodeDecodeError:
                pass

            taco = readbuffer.split("\n")
            readbuffer = taco.pop()
            for line in taco:
                if("PRIVMSG" in line):
                    c, username = get_data_from_line(line, self.channels_list)

                    if c is None or username is None:
                        continue
                    
                    #save the channel and username
                    if self.channel not in data.keys():
                        data[self.channel] = []
                    if username not in data[self.channel]:
                        data[self.channel].append(username)

                elif("PING" in line):
                    irc.send(("PONG %s\r\n" % line[1]).encode())
                    # print(f"\t\tPONG {self.channel}")
        
        irc.close()
        return


def kill_threads(thread_list: list):
    # kill all the threads
    for i, t in enumerate(thread_list):
        t.stop()
        time.sleep(0.5)     # wait because when the thread was launched it waited 0.5 seconds from the previous thread

    # wait for all the threads to finish
    for i, t in enumerate(thread_list):
        t.join()
        # print(f"\t\t THREAD {i+1} / {len(thread_list)} KILLED")


def save_and_restart(scheduler, thread_list: list):
    global data, t_killer_thread

    print("\t\t KILLING THREADS")
    # wait if the killer thread of the previous iteration is still running
    if t_killer_thread is not None and t_killer_thread.is_alive():
        print("\t\t WAITING FOR THE KILLER THREAD OF THE PREVIOUS ITERATION TO FINISH")
    if t_killer_thread is not None:
        t_killer_thread.join()

    # launch a thread to join all the others threads
    t_killer_thread = threading.Thread(target=kill_threads, args=(thread_list,))
    t_killer_thread.start()

    # save the data
    filename = f"dumps/{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.json"
    print(f"\t\t SAVING CHATTERS IN {filename}")
    
    remove_known_bots() # remove known bots
    
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
    print("\t\t LAUNCHING THREADS")
    for channel in channels_list:
        t = ListenChatThread(channel, channels_list)
        t.start()
        thread_list.append(t)
        time.sleep(0.5)     # wait to avoid the unsuccessful login error (probably for too many requests)
    
    print("\t\t THREADS LAUNCHED")

    return thread_list


def main():
    thread_list = launch_threads()

    # launch a scheduler to save the data and restart the threads
    my_scheduler = sched.scheduler(time.time, time.sleep)
    my_scheduler.enter(RESTART_TIME, 1, save_and_restart, (my_scheduler, thread_list))
    my_scheduler.run()


if __name__ == "__main__":
    main()
