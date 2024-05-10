import os
import json
from datetime import datetime
import itertools
import progressbar

MONTHS = ["december","january","february","march"]


def get_top_streamers(number_of_streamers):
    top_streamers = []

    with open('analysis_results/top_streamers.json', 'r') as f:
        top_streamers = json.load(f)

    # take only the first number_of_streamers streamers
    top_streamers = dict(itertools.islice(top_streamers.items(), number_of_streamers))

    return top_streamers


def get_unique_chatters_count(): 
    chatters_set = set()

    chatters_filenames = [x for x in os.listdir("chatters") if "template" not in x]

    print("> Counting unique chatters")

    bar = progressbar.ProgressBar(maxval=len(chatters_filenames), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, filename in enumerate(chatters_filenames):
        with open(f'chatters/{filename}', 'r') as f:
            chatters = json.load(f)

        for channel in chatters:
            chatters_set.update(chatters[channel])

        bar.update(i + 1)

    bar.finish()

    return len(chatters_set)


def get_chatters(top_streamers):
    chatters = {}

    chatters_filenames = [x for x in os.listdir("chatters") if "template" not in x]

    # filter only the chatters files of months in MONTHS
    chatters_filenames = [x for x in chatters_filenames if datetime.strptime(x.split("_")[0], '%Y%m%d').strftime('%B').lower() in MONTHS]


    print("> Getting chatters")

    bar = progressbar.ProgressBar(maxval=len(chatters_filenames), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, filename in enumerate(chatters_filenames):
        with open(f'chatters/{filename}', 'r') as f:
            chatters_dict = json.load(f)

        for channel in chatters_dict:
            if channel not in chatters:
                chatters[channel] = []

            if channel in top_streamers and channel in chatters_dict:
                chatters[channel] += chatters_dict[channel]

        bar.update(i + 1)

    bar.finish()

    # remove duplicates
    for channel in chatters:
        chatters[channel] = list(set(chatters[channel]))

    return chatters


def get_streamer_reach(top_streamers, unique_chatters_count):
    streamer_reach = {}

    chatters = get_chatters(top_streamers)

    for streamer in top_streamers:
        streamer_reach[streamer] = round((len(chatters[streamer]) / unique_chatters_count)*100, 4)

    return streamer_reach


def main():
    top_streamers = get_top_streamers(number_of_streamers=100)

    unique_chatters_count = get_unique_chatters_count()

    streamer_reach = get_streamer_reach(list(top_streamers.keys()), unique_chatters_count)

    with open('analysis_results/streamer_reach.csv', 'w') as f:
        f.write("Streamer\tReach\n")
        for streamer in streamer_reach:
            f.write(f"({int(top_streamers[streamer])}) {streamer}\t{streamer_reach[streamer]}%\n")


if __name__ == "__main__":
    main()
