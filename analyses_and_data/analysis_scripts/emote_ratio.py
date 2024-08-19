import os
import json
from datetime import datetime
import progressbar

KNOWN_BOTS = ['Nightbot', 'StreamElements', 'Streamlabs', 'Moobot', "Fossabot", "SonglistBot", "Wizebot"]
ANALYSES_REQUIRED = ["top_streamers"]


def get_top_streamers(number_of_streamers, version):
    top_streamers = []

    with open(f'analyses_and_data/cached_data/top_streamers{version}.txt', 'r') as f:
        lines = f.readlines()[0:number_of_streamers]

    for l in lines:
        top_streamers.append(l.strip())

    return top_streamers


def get_year_month_from_chat_filename(filename):
    dt =  datetime.strptime(filename, "chat_%y-%m-%d_%H-%M-%S.txt")
    return dt.strftime("%Y%m")


def get_emotes(channel, all_emotes):
    # get the emotes for the channel for every service and add the global emotes
    curr_emotes = []
    for service in all_emotes[channel]:
        curr_emotes.extend(all_emotes[channel][service])

    for service in all_emotes["global"]:
        curr_emotes.extend(all_emotes["global"][service])

    curr_emotes = list(set(curr_emotes))

    return curr_emotes


def get_emote_ratio(top_streamers: list, years_months: list):
    emote_ratio = {}    # emote_ratio = {"channel1" : 14, "channel2" : 7, "channel3" : 21, ...}
    total_meassages = {}    # key: channel, value: total number of messages, "total" key for the total number of messages

    # load all the emotes
    with open('analyses_and_data/downloaded_emotes.json', 'r') as f:
        all_emotes = json.load(f)
    emotes_channels = list(all_emotes.keys())

    # get the channels that are in both top_streamers and emotes_channels
    channels = [channel for channel in top_streamers if channel in emotes_channels]

    for i, channel in enumerate(channels):
        print(f"Calculating emote ratio for {channel}, {i + 1} of {len(channels)}")

        if channel == "global":
            continue

        # get only the emotes for the channel
        curr_emotes = get_emotes(channel, all_emotes)

        emote_ratio[channel] = 0
        total_meassages[channel] = 0

        # get the chats filenames for the channel
        chats_filenames = os.listdir(f'analyses_and_data/downloaded_chats/{channel}')
        chats_filenames = [filename for filename in chats_filenames if "template" not in filename]

        # chats_filenames = chats_filenames[::2]  # get one chat file every 2 files to speed up the process

        bar = progressbar.ProgressBar(maxval=len(chats_filenames), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()

        for j, chat_filename in enumerate(chats_filenames):
            if get_year_month_from_chat_filename(chat_filename) not in years_months:
                continue

            with open(f'analyses_and_data/downloaded_chats/{channel}/{chat_filename}', 'r') as f:
                lines = f.readlines()

            messages = lines[::5]

            for m in messages:
                try:
                    message = m.split("\t")[3].strip()
                    chatter = m.split("\t")[4].strip()
                except:
                    print(f"Error decoding message in {chat_filename} for {channel}, message: {m}")
                    continue

                if chatter in KNOWN_BOTS:   # ignore messages from known bots
                    continue

                total_meassages[channel] = total_meassages.get(channel, 0) + 1
                total_meassages["total"] = total_meassages.get("total", 0) + 1

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
        if total_meassages[channel] == 0:
            emote_ratio[channel] = 0
        else:
            emote_ratio[channel] = round((emote_ratio[channel] / total_meassages[channel]) * 100, 2)

    # sort the dictionary by value
    emote_ratio = dict(sorted(emote_ratio.items(), key=lambda item: item[1], reverse=True))

    # put the total at the start
    emote_ratio = {"total": emote_ratio["total"], **emote_ratio}

    return emote_ratio


def for_handler(years_months, version):
    top_streamers = get_top_streamers(60, version)

    result_str = ""

    emote_ratio = get_emote_ratio(top_streamers, years_months)

    result_str += "channel\tratio\n"
    for channel in emote_ratio:
        if channel == "total":
            continue

        result_str += f"{channel}\t{emote_ratio[channel]}\n"

    return result_str


def main():
    years_months = ["202401", "202402", "202403"]
    version = "202401-202403"

    top_streamers = get_top_streamers(60, version)

    emote_ratio = get_emote_ratio(top_streamers, years_months)

    # save emote_ratio to a csv file
    with open('analyses_and_data/analysis_results/emote_ratio.csv', 'w') as f:
        f.write("channel\tratio\n")
        for channel in emote_ratio:
            f.write(f"{channel}\t{emote_ratio[channel]}\n")


if __name__ == "__main__":
    main()
