import os
import json
from datetime import datetime
import progressbar
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', "data_downloader"))
from config import *

MONTHS = ["december","january","february","march"]


def get_top_streamers(number_of_streamers):
    top_streamers = []

    with open('top_streamers.txt', 'r') as f:
        lines = f.readlines()[0:number_of_streamers]

    for l in lines:
        top_streamers.append(l.strip())

    return top_streamers


def get_emote_ratio(top_streamers: list):
    emote_ratio = {}
    # emote_ratio = {"channel1" : 14, "channel2" : 7, "channel3" : 21, ...}

    total_meassages = {}    # key: channel, value: total number of messages, "total" key for the total number of messages

    with open('downloaded_emotes.json', 'r') as f:
        emotes = json.load(f)

    emotes_channels = list(emotes.keys())
    channels = [channel for channel in top_streamers if channel in emotes_channels]

    for i, channel in enumerate(channels):
        print(f"Calculating emote ratio for {channel}, {i + 1} of {len(channels)}")

        if channel == "global":
            continue

        emote_ratio[channel] = 0

        # get the chats filenames for the channel
        chats_filenames = os.listdir(f'downloaded_chats/{channel}')
        chats_filenames = [filename for filename in chats_filenames if "template" not in filename]

        chats_filenames = [x for x in chats_filenames if datetime.strptime(x.split("_")[1], '%y-%m-%d').strftime('%B').lower() in MONTHS]

        bar = progressbar.ProgressBar(maxval=len(chats_filenames), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()

        for j, chat_filename in enumerate(chats_filenames):
            with open(f'downloaded_chats/{channel}/{chat_filename}', 'r') as f:
                lines = f.readlines()

            messages = []
            for i, line in enumerate(lines):
                try:
                    messages.append((line.split("\t")[3].strip(), line.split("\t")[4].strip()))
                except:
                    print(f"Error decoding message in {chat_filename} for {channel}, row: {i}, message: {line}")

            messages = messages[::5]   # get every 5th message to speed up the process

            for chatter, message in messages:
                if chatter in KNOWN_BOTS:   # ignore messages from known bots
                    continue

                total_meassages[channel] = total_meassages.get(channel, 0) + 1
                total_meassages["total"] = total_meassages.get("total", 0) + 1

                # get the emotes for the channel for every service and add the global emotes
                curr_emotes = []
                for service in emotes[channel]:
                    for emote in emotes[channel][service]:
                        curr_emotes.append(emote)

                for service in emotes["global"]:
                    for emote in emotes["global"][service]:
                        curr_emotes.append(emote)

                curr_emotes = list(set(curr_emotes))

                for emote in curr_emotes:
                    message = message.strip()
                    if message.startswith(emote) or message.endswith(emote) or " "+emote+" " in message:
                        emote_ratio[channel] += 1
                        break

            bar.update(j + 1)

        bar.finish()

    # calculate the ratio
    emote_ratio["total"] = 0
    for channel in emote_ratio:
        emote_ratio["total"] += emote_ratio[channel]
    emote_ratio["total"] = round((emote_ratio["total"] / total_meassages["total"]) * 100, 2)

    for channel in emote_ratio:
        if channel == "total":
            continue
        emote_ratio[channel] = round((emote_ratio[channel] / total_meassages[channel]) * 100, 2)

    # sort the dictionary by value
    emote_ratio = dict(sorted(emote_ratio.items(), key=lambda item: item[1], reverse=True))

    # put the total at the start
    emote_ratio = {"total": emote_ratio["total"], **emote_ratio}

    return emote_ratio


def main():
    top_streamers = get_top_streamers(100)

    emote_ratio = get_emote_ratio(top_streamers)

    # save emote_ratio to a csv file
    with open('analysis_results/emote_ratio.csv', 'w') as f:
        f.write("channel\tratio\n")
        for channel in emote_ratio:
            f.write(f"{channel}\t{emote_ratio[channel]}\n")


if __name__ == "__main__":
    main()
