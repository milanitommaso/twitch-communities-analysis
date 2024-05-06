import json
import itertools
from datetime import datetime
import os
import progressbar

MONTHS = ["december","january","february","march"]

def get_top_streamers(number_of_streamers):
    top_streamers = []

    with open('analysis_results/top_streamers.json', 'r') as f:
        top_streamers = json.load(f)

    # sort the streamers by average viewers
    top_streamers = {k: v for k, v in sorted(top_streamers.items(), key=lambda item: item[1], reverse=True)}

    # take only the first number_of_streamers streamers
    top_streamers = dict(itertools.islice(top_streamers.items(), number_of_streamers))

    return top_streamers


def get_chatters(top_streamers):
    chatters = {}

    chatters_filenames = [x for x in os.listdir("chatters") if "template" not in x]

    # filter only the chatters files of months in MONTHS
    chatters_filenames = [x for x in chatters_filenames if datetime.strptime(x.split("_")[0], '%Y%m%d').strftime('%B').lower() in MONTHS]

    print("> Getting chatters")

    bar = progressbar.ProgressBar(maxval=len(chatters_filenames) , widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, filename in enumerate(chatters_filenames):
        with open(f'chatters/{filename}', 'r') as f:
            chatters_dict = json.load(f)

        for channel in chatters_dict:
            if channel in top_streamers and channel not in chatters:
                chatters[channel] = []

            if channel in top_streamers and channel in chatters_dict:
                chatters[channel] += chatters_dict[channel]

        bar.update(i + 1)

    bar.finish()

    # remove duplicates
    for channel in chatters:
        chatters[channel] = list(set(chatters[channel]))

    return chatters


def get_watched_channels(top_streamers):
    chatters = get_chatters(top_streamers)
    all_chatters = list(itertools.chain.from_iterable(chatters.values()))

    print("> Getting counter")
    bar = progressbar.ProgressBar(maxval=len(all_chatters) , widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    counter = {}
    for i, chatter in enumerate(all_chatters):
        bar.update(i + 1)

        if chatter not in counter:
            counter[chatter] = 0

        counter[chatter] += 1
    
    bar.finish()

    watched_channels = {}

    print("> Getting watched channels")

    bar = progressbar.ProgressBar(maxval=len(counter) , widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, chatter in enumerate(counter.keys()):
        n_channels = counter[chatter]

        if str(n_channels) not in watched_channels:
            watched_channels[str(n_channels)] = 0

        watched_channels[str(n_channels)] += 1


        bar.update(i + 1)

    bar.finish()

    # sort by key
    watched_channels = {k: v for k, v in sorted(watched_channels.items(), key=lambda item: int(item[0]))}    

    return watched_channels


def main():
    top_streamers = get_top_streamers(5000)

    watched_channels = get_watched_channels(list(top_streamers.keys()))

    with open('analysis_results/watched_channels.csv', 'w') as f:
        f.write("n_channels\tn_chatters\n")
        for n_channels, n_chatters in watched_channels.items():
            f.write(f"{n_channels}\t{n_chatters}\n")


if __name__ == "__main__":
    main()
