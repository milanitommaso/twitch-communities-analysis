import os
import json
import progressbar
from datetime import datetime

ANALYSES_REQUIRED = ["top_streamers", "lives"]
MINUTES_AFTER_START = 60


streams_info_files = [f for f in os.listdir('analyses_and_data/streams_info') if not f.startswith('.') and 'template' not in f.lower()]
streams_info_files.sort()


def get_top_streamers(number_of_streamers, version):
    top_streamers = []

    with open(f'analyses_and_data/cached_data/top_streamers{version}.json', 'r') as f:
        top_streamers = json.load(f)

    # take the first number_of_streamers streamers
    top_streamers = {k: v for k, v in top_streamers.items() if v > 0}
    top_streamers = dict(sorted(top_streamers.items(), key=lambda item: item[1], reverse=True))
    top_streamers = {k: v for k, v in list(top_streamers.items())[:number_of_streamers]}

    return top_streamers


def get_viewers_after_start(channel: str, start):
    filename_start = f"analyses_and_data/streams_info/streams_info{start}.txt"

    # get the streams_info files from the start timestamp to sart imestamp + 60 minutes
    
    for i, file in enumerate(streams_info_files):
        if "analyses_and_data/streams_info/" + file == filename_start:
            break
    files = streams_info_files[i:i+MINUTES_AFTER_START+1]   # take the next 60 files (60 minutes)

    # get the viewers for the channel
    viewers = []
    for file in files:
        with open(f'analyses_and_data/streams_info/{file}', 'r') as f:
            for line in f:
                c, cat, v = line.strip().split('\t')
                if c == channel:
                    viewers.append(int(v))
                    break

    # normalize the viewers list
    viewers = [v / viewers[-1] for v in viewers]

    return viewers


def get_streams_start(top_streamers: list, years_months, version):
    top_streamers_list = list(top_streamers.keys())

    # open the lives.txt file
    with open(f'analyses_and_data/cached_data/lives{version}.txt', 'r') as f:
        lives = f.readlines()

    mean_viewers_after_start = {}   # key: minutes after start, value: list of viewers after start
    for i in range(MINUTES_AFTER_START+1):
        mean_viewers_after_start[i] = []

    bar = progressbar.ProgressBar(maxval=len(lives), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    for i, line in enumerate(lives):
        bar.update(i+1)
        channel, start, end = line.strip().split('\t')

        if channel not in top_streamers_list:
            continue

        # check that the end of the live is in a month in MONTHS
        end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        if end.strftime('%Y%m').lower() not in years_months:
            continue

        # get the viewers after the start timestamp
        viewers = get_viewers_after_start(channel, start.replace(":", "-").replace(" ", "_"))

        # add the viewers to the mean_viewers_after_start
        for j, v in enumerate(viewers):
            mean_viewers_after_start[j].append(v)

    bar.finish()

    # calculate the mean viewers after start
    for i in range(MINUTES_AFTER_START+1):
        if len(mean_viewers_after_start[i]) == 0:
            mean_viewers_after_start[i] = 0
        else:
            mean_viewers_after_start[i] = sum(mean_viewers_after_start[i]) / len(mean_viewers_after_start[i])

    return mean_viewers_after_start


def for_handler(years_months, version):
    result_str = ""

    top_streamers = get_top_streamers(100, version)

    mean_viewers_after_start = get_streams_start(top_streamers, years_months, version)

    result_str += "minutes_after_start\tmean_viewers\n"
    for i in range(MINUTES_AFTER_START+1):
        result_str += f"{i}\t{mean_viewers_after_start[i]*100}\n"

    return result_str


def main():
    top_streamers = get_top_streamers(100)

    mean_viewers_after_start = get_streams_start(top_streamers)

    with open('analysis_results/mean_viewers_after_start.csv', 'w') as f:
        f.write("minutes_after_start\tmean_viewers\n")
        for i in range(MINUTES_AFTER_START+1):
            f.write(f"{i}\t{mean_viewers_after_start[i]}\n")


if __name__ == "__main__":
    main()
