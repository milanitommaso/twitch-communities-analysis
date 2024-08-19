import os
import json
from datetime import datetime
import itertools
import progressbar

ANALYSES_REQUIRED = ["top_streamers"]


def get_top_streamers(number_of_streamers, version):
    top_streamers = []

    with open(f'analyses_and_data/cached_data/top_streamers{version}.json', 'r') as f:
        top_streamers = json.load(f)

    # take only the first number_of_streamers streamers
    top_streamers = dict(itertools.islice(top_streamers.items(), number_of_streamers))

    return top_streamers


def get_year_month_from_chatters_filename(filename):
    dt =  datetime.strptime(filename, "%Y%m%d_%H%M.json")
    return dt.strftime("%Y%m")


def get_unique_chatters_count(years_months):
    # get unique chatters for all channels of all twitch italia

    chatters_set = set()

    chatters_filenames = [x for x in os.listdir("analyses_and_data/chatters") if "template" not in x]
    chatters_filenames_filtered = []

    for filename in chatters_filenames:
        if get_year_month_from_chatters_filename(filename) in years_months:
            chatters_filenames_filtered.append(filename)

    chatters_filenames = chatters_filenames_filtered

    print("> Counting unique chatters")

    bar = progressbar.ProgressBar(maxval=len(chatters_filenames), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, filename in enumerate(chatters_filenames):
        with open(f'analyses_and_data/chatters/{filename}', 'r') as f:
            chatters = json.load(f)

        for channel in chatters:
            chatters_set.update(chatters[channel])

        bar.update(i + 1)

    bar.finish()

    return len(chatters_set)


def get_chatters(top_streamers, years_months):
    chatters = {}

    chatters_filenames = [x for x in os.listdir("analyses_and_data/chatters") if "template" not in x]
    chatters_filenames_filtered = []

    for filename in chatters_filenames:
        if get_year_month_from_chatters_filename(filename) in years_months:
            chatters_filenames_filtered.append(filename)

    chatters_filenames = chatters_filenames_filtered

    print("> Getting chatters")

    bar = progressbar.ProgressBar(maxval=len(chatters_filenames), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, filename in enumerate(chatters_filenames):
        with open(f'analyses_and_data/chatters/{filename}', 'r') as f:
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


def get_streamer_reach(top_streamers, unique_chatters_count, years_months):
    streamer_reach = {}

    chatters = get_chatters(top_streamers, years_months)

    for streamer in top_streamers:
        if streamer not in chatters:
            streamer_reach[streamer] = 0
            continue
        streamer_reach[streamer] = round((len(chatters[streamer]) / unique_chatters_count)*100, 4)

    return streamer_reach


def for_handler(years_months, version):
    result_str = ""

    top_streamers = get_top_streamers(60, version)

    unique_chatters_count = get_unique_chatters_count(years_months)

    streamer_reach = get_streamer_reach(list(top_streamers.keys()), unique_chatters_count, years_months)

    result_str += "Streamer\tReach\n"
    for streamer in streamer_reach:
        result_str += f"({int(top_streamers[streamer])}) {streamer}\t{streamer_reach[streamer]}%\n"

    return result_str


def main():
    years_months = ["202404", "202405", "202406"]
    version = "202404-202406"

    top_streamers = get_top_streamers(60, version)

    unique_chatters_count = get_unique_chatters_count(years_months)

    streamer_reach = get_streamer_reach(list(top_streamers.keys()), unique_chatters_count)

    with open('analysis_results/streamer_reach.csv', 'w') as f:
        f.write("Streamer\tReach\n")
        for streamer in streamer_reach:
            f.write(f"({int(top_streamers[streamer])}) {streamer}\t{streamer_reach[streamer]}%\n")


if __name__ == "__main__":
    main()
