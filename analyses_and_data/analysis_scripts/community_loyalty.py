from datetime import datetime
import os
import json
import itertools
import progressbar

N_CHANNELS = 60
ANALYSES_REQUIRED = ["top_streamers"]


def get_top_streamers(number_of_streamers, version):
    top_streamers = []

    with open(f'analyses_and_data/cached_data/top_streamers{version}.json', 'r') as f:
        top_streamers = json.load(f)

    # sort the streamers by average viewers
    top_streamers = {k: v for k, v in sorted(top_streamers.items(), key=lambda item: item[1], reverse=True)}

    # take only the first number_of_streamers streamers
    top_streamers = dict(itertools.islice(top_streamers.items(), number_of_streamers))

    return top_streamers


def get_year_month_from_chatters_filename(filename):
    dt =  datetime.strptime(filename, "%Y%m%d_%H%M.json")
    return dt.strftime("%Y%m")


def get_chatters(top_streamers, years_months):
    chatters = {}

    chatters_filenames = sorted([x for x in os.listdir("analyses_and_data/chatters") if "template" not in x])

    print("> Getting chatters")

    bar = progressbar.ProgressBar(maxval=len(chatters_filenames) , widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, filename in enumerate(chatters_filenames):

        year_month = get_year_month_from_chatters_filename(filename)
        if not year_month in years_months:
            continue

        with open(f'analyses_and_data/chatters/{filename}', 'r') as f:
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

    # order the dictionary using the order of top streamers
    chatters_ordered = {}
    for streamer in top_streamers:
        if streamer in chatters:
            chatters_ordered[streamer] = chatters[streamer]

    return chatters_ordered


def get_counter(all_chatters):
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

    return counter


def get_community_loyalty(years_months, version):
    top_streamers = list(get_top_streamers(10000, version))

    chatters = get_chatters(top_streamers, years_months)
    all_chatters = list(itertools.chain.from_iterable(chatters.values()))

    counter = get_counter(all_chatters)

    community_loyalty = {}

    print("> Calculating community loyalty")

    bar = progressbar.ProgressBar(maxval=N_CHANNELS, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, channel in enumerate(chatters):
        bar.update(i)

        if i == N_CHANNELS:
            break

        for chatter in chatters[channel]:
            # find the number of channels that the chatter is in
            n_channels = counter[chatter]

            if channel not in community_loyalty:
                community_loyalty[channel] = {}

            if n_channels not in community_loyalty[channel]:
                community_loyalty[channel][n_channels] = 0

            community_loyalty[channel][n_channels] += 1

        community_loyalty[channel] = {k: (v / len(chatters[channel]))*100 for k, v in community_loyalty[channel].items()}

    bar.finish()

    return community_loyalty


def for_handler(years_months, version):
    community_loyalty = get_community_loyalty(years_months, version)

    result_str = ""

    for i in range(1, 21):
        for streamer in community_loyalty:
            if i not in community_loyalty[streamer]:
                community_loyalty[streamer][i] = 0

    result_str += "Streamer\t1\t2-3\t4-5\t6-10\t11-15\t16-20\t21+\n"
    for streamer in community_loyalty:
        result_str += f"{streamer}\t"

        result_str += f"{round(community_loyalty[streamer][1], 3)}%\t"

        result_str += f"{round(community_loyalty[streamer][2] + community_loyalty[streamer][3], 3)}%\t"

        result_str += f"{round(community_loyalty[streamer][4] + community_loyalty[streamer][5], 3)}%\t"

        result_str += f"{round(community_loyalty[streamer][6] + community_loyalty[streamer][7] + community_loyalty[streamer][8] + community_loyalty[streamer][9] + community_loyalty[streamer][10], 3)}%\t"

        result_str += f"{round(community_loyalty[streamer][11] + community_loyalty[streamer][12] + community_loyalty[streamer][13] + community_loyalty[streamer][14] + community_loyalty[streamer][15], 3)}%\t"

        result_str += f"{round(community_loyalty[streamer][16] + community_loyalty[streamer][17] + community_loyalty[streamer][18] + community_loyalty[streamer][19] + community_loyalty[streamer][20], 3)}%\t"

        result_str += f"{round(sum([v for k, v in community_loyalty[streamer].items() if k > 20]), 3)}%\n"

    return result_str


def main():
    community_loyalty = get_community_loyalty(["202401", "202402", "202403"])

    for i in range(1, 21):
        for streamer in community_loyalty:
            if i not in community_loyalty[streamer]:
                community_loyalty[streamer][i] = 0

    with open('analyses_and_data/analysis_results/community_loyalty.csv', 'w') as f:
        f.write("Streamer\t1\t2-3\t4-5\t6-10\t11-15\t16-20\t21+\n")
        for streamer in community_loyalty:
            f.write(f"{streamer}\t")
            f.write(f"{round(community_loyalty[streamer][1], 3)}%\t")

            f.write(f"{round(community_loyalty[streamer][2] + community_loyalty[streamer][3], 3)}%\t")

            f.write(f"{round(community_loyalty[streamer][4] + community_loyalty[streamer][5], 3)}%\t")

            f.write(f"{round(community_loyalty[streamer][6] + community_loyalty[streamer][7] + community_loyalty[streamer][8] + community_loyalty[streamer][9] + community_loyalty[streamer][10], 3)}%\t")

            f.write(f"{round(community_loyalty[streamer][11] + community_loyalty[streamer][12] + community_loyalty[streamer][13] + community_loyalty[streamer][14] + community_loyalty[streamer][15], 3)}%\t")

            f.write(f"{round(community_loyalty[streamer][16] + community_loyalty[streamer][17] + community_loyalty[streamer][18] + community_loyalty[streamer][19] + community_loyalty[streamer][20], 3)}%\t")

            f.write(f"{round(sum([v for k, v in community_loyalty[streamer].items() if k > 20]), 3)}%\n")
    

if __name__ == "__main__":
    main()
