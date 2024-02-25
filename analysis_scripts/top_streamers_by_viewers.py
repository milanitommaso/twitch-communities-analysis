import os
from datetime import datetime

def get_lives_count():
    lives = {}

    with open("lives.txt", "r") as file:
        lines = file.readlines()
    for line in lines:
        channel = line.split("\t")[0].strip()
        if channel not in lives:
            lives[channel] = 0
        lives[channel] += 1

    return lives


def get_top_streamers_by_viewers():
    top_streamers = {}  # key: streamer, value: average viewers

    # get all streams info filenames
    streams_info = [x for x in os.listdir("streams_info") if "template" not in x]
    streams_info.sort()

    streams_info = streams_info[::5]  # take every 5th file to reduce the number of files to process

    for streams in streams_info:
        print(streams)
        with open("streams_info/" + streams, "r") as file:
            lines = file.readlines()
        for line in lines:
            streamer = line.split("\t")[0].strip()
            viewers = int(line.split("\t")[2].strip())

            if streamer not in top_streamers:
                top_streamers[streamer] = []
            top_streamers[streamer].append(viewers)

    # calculate the average viewers for each streamer and check that the streamers has made at least 10 live streams
    lives_count = get_lives_count()
    for streamer in list(top_streamers.keys()):
        if streamer not in lives_count or lives_count[streamer] < 10:
            del top_streamers[streamer]
        else:
            top_streamers[streamer] = sum(top_streamers[streamer]) / len(top_streamers[streamer])

    # sort the streamers by average viewers
    top_streamers = {k: v for k, v in sorted(top_streamers.items(), key=lambda item: item[1], reverse=True)}

    return top_streamers


def main():
    top_streamers = get_top_streamers_by_viewers()

    # save the top streamers to a txt file
    with open("top_streamers.txt", "w") as file:
        for streamer in top_streamers.keys():
            file.write(f"{streamer}\n")


if __name__ == "__main__":
    main()
