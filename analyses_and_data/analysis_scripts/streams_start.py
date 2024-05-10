import os
import json
import progressbar
from datetime import datetime

MINUTES_AFTER_START = 60
MONTHS = ["december","january","february","march"]


def get_top_streamers(number_of_streamers):
    top_streamers = []

    with open('analysis_results/top_streamers.json', 'r') as f:
        top_streamers = json.load(f)

    # take the first number_of_streamers streamers
    top_streamers = {k: v for k, v in top_streamers.items() if v > 0}
    top_streamers = dict(sorted(top_streamers.items(), key=lambda item: item[1], reverse=True))
    top_streamers = {k: v for k, v in list(top_streamers.items())[:number_of_streamers]}

    return top_streamers


def get_viewers_after_start(channel: str, start, average_viewers: float):
    filename_start = f"streams_info/streams_info{start}.txt"

    # get the streams_info files from the start timestamp to sart imestamp + 60 minutes
    files = [f for f in sorted(os.listdir('streams_info')) if not f.startswith('.') and 'template' not in f.lower()]
    files.sort()
    for i, file in enumerate(files):
        if "streams_info/" + file == filename_start:
            break
    files = files[i:i+MINUTES_AFTER_START+1]   # take the next 60 files (60 minutes)

    # get the viewers for the channel
    viewers = []
    for file in files:
        with open(f'streams_info/{file}', 'r') as f:
            for line in f:
                c, cat, v = line.strip().split('\t')
                if c == channel:
                    viewers.append(int(v))
                    break

    # normalize the viewers list
    viewers = [v / viewers[-1] for v in viewers]

    return viewers


def get_streams_start(top_streamers: list):
    top_streamers_list = list(top_streamers.keys())

    # open the lives.txt file
    with open('lives.txt', 'r') as f:
        lives = f.readlines()

    mean_viewers_after_start = {}   # key: minutes after start, value: list of viewers after start
    for i in range(MINUTES_AFTER_START+1):
        mean_viewers_after_start[i] = []


    bar = progressbar.ProgressBar(maxval=len(lives), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    for i, line in enumerate(lives):
        bar.update(i+1)
        channel, start, end = line.strip().split('\t')

        # check that the end of the live is in a month in MONTHS
        end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        if end.strftime('%B').lower() not in MONTHS:
            continue

        if channel not in top_streamers_list:
            continue

        # get the viewers after the start timestamp
        viewers = get_viewers_after_start(channel, start.replace(":", "-").replace(" ", "_"), top_streamers[channel])


        # add the viewers to the mean_viewers_after_start
        for j, v in enumerate(viewers):
            mean_viewers_after_start[j].append(v)

    bar.finish()

    # calculate the mean viewers after start
    for i in range(MINUTES_AFTER_START+1):
        mean_viewers_after_start[i] = sum(mean_viewers_after_start[i]) / len(mean_viewers_after_start[i])

    return mean_viewers_after_start


def main():
    top_streamers = get_top_streamers(100)

    mean_viewers_after_start = get_streams_start(top_streamers)

    with open('analysis_results/mean_viewers_after_start.csv', 'w') as f:
        f.write("minutes_after_start\tmean_viewers\n")
        for i in range(MINUTES_AFTER_START+1):
            f.write(f"{i}\t{mean_viewers_after_start[i]}\n")



if __name__ == "__main__":
    main()
