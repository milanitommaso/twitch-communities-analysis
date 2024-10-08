import os
import json
from datetime import datetime, timedelta
import progressbar
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', "data_downloader"))
from notify_telegram import notify_error

CHATTERS_FOLDER = "chatters"

# Rounds to nearest hour by adding a timedelta hour if minute >= 30
def hour_rounder(t):
    return t.replace(second=0, microsecond=0, minute=0, hour=t.hour) + timedelta(hours=t.minute//30)


# create a file every hour that contain all the chatters for a channel for that hour, take the data from the downloaded chats
def download_chatters():
    # read the last datetime processed
    try:
        with open('analysis_scripts/get_chatters.json', 'r') as f:
            last_end_datetime = datetime.strptime(json.load(f)["last_end_datetime"], '%Y-%m-%d %H-%M-%S')
    except:
        print("> Error, no file found")
        notify_error("get_chatters.py - No file found for last datetime processed")

    current_start_datetime = hour_rounder(last_end_datetime)
    current_end_datetime = last_end_datetime + timedelta(hours=1)
    end_datetime = last_end_datetime + timedelta(days=1)

    # get all the dirs representing the channels
    files = list(os.listdir('downloaded_chats'))
    dirs = [x for x in files if os.path.isdir(os.path.join('downloaded_chats', x))]


    while current_end_datetime <= hour_rounder(end_datetime):
        print(f"> Processing {current_start_datetime.strftime('%Y-%m-%d-%H')}")

        chatters = {}

        bar = progressbar.ProgressBar(maxval=len(dirs), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()

        # for each dir, get all the files representing the chats
        for i, d in enumerate(dirs):
            files = list(os.listdir(os.path.join('downloaded_chats', d)))

            # for each file, open it and save the chatters in a dict
            for f in files:
                # if the file has been created after the end datetime, skip the file
                if datetime.strptime(f.split('.')[0].replace("chat_", ""), '%y-%m-%d_%H-%M-%S') > current_end_datetime:
                    continue


                with open(os.path.join('downloaded_chats', d, f), 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                
                # if the timestamp of the last line is before the start datetime, skip the file
                try:
                    last_line = lines[-1]
                except:
                    continue

                last_ts = last_line.split('\t')[0]
                if datetime.strptime(last_ts, '%y-%m-%d_%H-%M-%S') < current_start_datetime:
                    continue

                j = 0
                while j < len(lines):
                    try:
                        # get the timestamp of the message
                        ts = lines[j].split('\t')[0]
                        # get the chatter
                        chatter = lines[j].split('\t')[3]
                    except:
                        j += 1
                        continue

                    ts = datetime.strptime(ts, '%y-%m-%d_%H-%M-%S')
                    
                    if ts < current_start_datetime:
                        j += 50
                        continue
                    elif ts > current_end_datetime:
                        break
                
                    if d not in chatters:
                        chatters[d] = set()
                    chatters[d].add(chatter)

                    j += 1

            bar.update(i+1)

        bar.finish()

        # save the chatters in a file
        filename = os.path.join(CHATTERS_FOLDER, current_start_datetime.strftime('%Y%m%d_%H%M')) + '.json'
        with open(filename, 'w') as f:
            chatters = {k: list(v) for k, v in chatters.items()}
            json.dump(chatters, f, indent=4)

        # increment the hour
        current_start_datetime += timedelta(hours=1)
        current_end_datetime += timedelta(hours=1)

    current_end_datetime -= timedelta(hours=1)  # remove the last increment

    # save the last datetime processed
    with open('analysis_scripts/get_chatters.json', 'w') as f:
        json.dump({"last_end_datetime": current_end_datetime.strftime('%Y-%m-%d %H-%M-%S')}, f, indent=4)

if __name__ == '__main__':
    download_chatters()
