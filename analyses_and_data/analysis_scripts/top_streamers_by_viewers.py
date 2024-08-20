import os
import progressbar
import json
from datetime import datetime

ANALYSES_REQUIRED = ["lives"]

def get_year_month_from_streams_info_filename(filename):
    dt =  datetime.strptime(filename, "streams_info%Y-%m-%d_%H-%M-%S.txt")
    return dt.strftime("%Y%m").lower()


def get_lives_count(years_months, version):
    lives = {}

    with open(f"analyses_and_data/cached_data/lives{version}.txt", "r") as file:
        lines = file.readlines()
    for line in lines:
        if datetime.strptime(line.split("\t")[1].strip(), "%Y-%m-%d %H:%M:%S").strftime("%Y%m").lower() not in years_months:
            continue

        channel = line.split("\t")[0].strip()
        if channel not in lives:
            lives[channel] = 0
        lives[channel] += 1

    return lives


def get_top_streamers_by_viewers(years_months, version):
    top_streamers = {}  # key: streamer, value: average viewers
    min_lives = 4 * len(years_months)  # the streamer must have made at least 4 live streams in each month

    # get all streams info filenames
    streams_info = [x for x in os.listdir("analyses_and_data/streams_info") if "template" not in x]
    streams_info.sort()

    streams_info = streams_info[::5]  # take every 5th file to reduce the number of files to process

    print(f"> Calculating the average viewers for each streamer and checking that the streamers has made at least {min_lives} live streams")

    bar = progressbar.ProgressBar(maxval=len(streams_info), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, streams in enumerate(streams_info):

        # check that the file is in the years_months
        if get_year_month_from_streams_info_filename(streams) not in years_months:
            bar.update(i + 1)
            continue

        with open("analyses_and_data/streams_info/" + streams, "r") as file:
            lines = file.readlines()
        for line in lines:
            streamer = line.split("\t")[0].strip()
            viewers = int(line.split("\t")[2].strip())

            if streamer not in top_streamers:
                top_streamers[streamer] = []
            top_streamers[streamer].append(viewers)

        bar.update(i + 1)

    bar.finish()

    # calculate the average viewers for each streamer and check that the streamers has made at least min_lives live streams
    lives_count = get_lives_count(years_months, version)
    for streamer in list(top_streamers.keys()):
        if streamer not in lives_count or lives_count[streamer] < min_lives:
            del top_streamers[streamer]
        else:
            top_streamers[streamer] = round(sum(top_streamers[streamer]) / len(top_streamers[streamer]), 2)

    # sort the streamers by average viewers
    top_streamers = {k: v for k, v in sorted(top_streamers.items(), key=lambda item: item[1], reverse=True)}

    return top_streamers


def get_streamer_count_by_viewers_slot(top_streamer):
    slots = ["0-19", "20-49", "50-99", "100-199", "200-499", "500-999", "1000-1999", "2000-"]

    # find how many streamers have the number of viewers in each slot

    streamer_count_by_viewers_slot = {slot: 0 for slot in slots}
    for streamer in top_streamer.keys():
        viewers = top_streamer[streamer]
        for slot in slots:
            n = slot.split("-")
            if len(n) == 2 and n[1] != "":
                n = int(n[1]) + 1
                if viewers < n:
                    streamer_count_by_viewers_slot[slot] += 1
                    break
            else:
                if viewers >= int(n[0]):
                    streamer_count_by_viewers_slot[slot] += 1
                    break

    return streamer_count_by_viewers_slot


def for_handler(years_months, version):
    top_streamers = get_top_streamers_by_viewers(years_months, version)

    return top_streamers


def main():
    top_streamers = get_top_streamers_by_viewers()

    streamer_count_by_viewers_slot = get_streamer_count_by_viewers_slot(top_streamers)

    # save the top streamers to a json file
    with open("analysis_results/top_streamers.json", "w") as file:
        json.dump(top_streamers, file, indent=4)

    # save the top streamers to a txt file
    with open("top_streamers.txt", "w") as file:
        for streamer in top_streamers.keys():
            file.write(f"{streamer}\n")


    # save the streamer count by viewers slot to a json file
    with open("analysis_results/streamer_count_by_viewers_slot.json", "w") as file:
        json.dump(streamer_count_by_viewers_slot, file, indent=4)


if __name__ == "__main__":
    main()
