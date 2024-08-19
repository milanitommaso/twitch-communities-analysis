import os
import progressbar
from datetime import datetime, timedelta
import json

ANALYSES_REQUIRED = ["lives_count"]

START_MORNING_TIMESLOT_STR = "07:00:00"
END_MORNING_TIMESLOT_STR = "12:59:59"
START_AFTERNOON_TIMESLOT_STR = "13:00:00"
END_AFTERNOON_TIMESLOT_STR = "18:59:59"
START_EVENING_TIMESLOT_STR = "19:00:00"
END_EVENING_TIMESLOT_STR = "00:59:59"
START_NIGHT_TIMESLOT_STR = "01:00:00"
END_NIGHT_TIMESLOT_STR = "06:59:59"


def get_datetime_from_streams_info_filename(filename):
    return datetime.strptime(filename, "streams_info%Y-%m-%d_%H-%M-%S.txt")


def get_year_month_from_streams_info_filename(filename):
    dt =  datetime.strptime(filename, "streams_info%Y-%m-%d_%H-%M-%S.txt")
    return dt.strftime("%Y%m").lower()


def get_timeslot(time) -> str:
    if time >= datetime.strptime(START_MORNING_TIMESLOT_STR, "%H:%M:%S").time() and time <= datetime.strptime(END_MORNING_TIMESLOT_STR, "%H:%M:%S").time():
        return "morning"
    elif time >= datetime.strptime(START_AFTERNOON_TIMESLOT_STR, "%H:%M:%S").time() and time <= datetime.strptime(END_AFTERNOON_TIMESLOT_STR, "%H:%M:%S").time():
        return "afternoon"
    elif time >= datetime.strptime(START_NIGHT_TIMESLOT_STR, "%H:%M:%S").time() and time <= datetime.strptime(END_NIGHT_TIMESLOT_STR, "%H:%M:%S").time():
        return "night"
    else:
        # the evening timeslot includes multiple days
        return "evening"


def get_timeslots_from_range(start, end) -> list:
    timeslot_list = []

    if start >= end:
        print("Error: start time is greater than or equal to end time")
        return

    timeslot = 0
    timeslot_prev = 0

    while start <= end:
        timeslot = get_timeslot(start.time())

        if timeslot != timeslot_prev:
            timeslot_list.append(timeslot)

        start += timedelta(minutes=10)

        timeslot_prev = timeslot

    return timeslot_list


def get_lives_count(version) -> dict:
    with open(f"analyses_and_data/cached_data/lives_count{version}.json", "r") as file:
        lives = json.load(file)

    return lives


def get_top_streamers_by_viewers_timeslots(years_months, min_total_lives, version):
    top_streamers = {}  # key: month, value: dict with key timeslot, value: dict with key: streamer, value: average viewers
    # top_streamers = {
    #     "january": {
    #         "morning": {
    #             "streamer1": [1254, 987, 993],
    #             "streamer2": [90, 112, 84, 73],
    #             ...
    #         },
    #         ...
    #     },
    #     ...
    # }

    lives_count = get_lives_count(version)

    # get all streams info filenames
    streams_info = [x for x in os.listdir("analyses_and_data/streams_info") if "template" not in x]
    streams_info.sort()

    streams_info = streams_info[::5]  # take every 5th file to reduce the number of files to process

    print("> Calculating top streamers by viewers for each timeslot")
    bar = progressbar.ProgressBar(maxval=len(streams_info), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, streams in enumerate(streams_info):
        bar.update(i + 1)

        datetime = get_datetime_from_streams_info_filename(streams)
        time = datetime.time()
        timeslot = get_timeslot(time)
        month = get_year_month_from_streams_info_filename(streams)

        if month not in years_months:
            continue

        with open("analyses_and_data/streams_info/" + streams, "r") as file:
            lines = file.readlines()

        for line in lines:
            streamer = line.split("\t")[0].strip()
            viewers = int(line.split("\t")[2].strip())
            
            if month not in top_streamers:
                top_streamers[month] = {}

            if timeslot not in top_streamers[month]:
                top_streamers[month][timeslot] = {}

            if streamer not in top_streamers[month][timeslot]:
                top_streamers[month][timeslot][streamer] = []
            top_streamers[month][timeslot][streamer].append(viewers)

    bar.finish()

    # calculate the mean for all months
    top_streamers["total"] = {}
    for month in top_streamers:
        if month == "total":
            continue
        for timeslot in top_streamers[month]:
            for streamer in top_streamers[month][timeslot]:
                if timeslot not in top_streamers["total"]:
                    top_streamers["total"][timeslot] = {}
                if streamer not in top_streamers["total"][timeslot]:
                    top_streamers["total"][timeslot][streamer] = []
                top_streamers["total"][timeslot][streamer].extend(top_streamers[month][timeslot][streamer])

    print("> Calculating average viewers for each streamer for each timeslot")
    bar = progressbar.ProgressBar(maxval=len(top_streamers), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    # calculate the average viewers for each month, timeslot and streamer
    for i, month in enumerate(top_streamers):

        for timeslot in top_streamers[month]:
            for streamer in top_streamers[month][timeslot]:
                # check if the streamer has at least made 10 lives per timeslot in the month or 30 lives in total
                if month == "total" and (streamer not in lives_count[timeslot] or lives_count[timeslot][streamer] < min_total_lives):
                    top_streamers[month][timeslot][streamer] = -1
                    continue
                if month != "total" and (streamer not in lives_count[timeslot] or lives_count[timeslot][streamer] < 10):
                    top_streamers[month][timeslot][streamer] = -1
                    continue
                top_streamers[month][timeslot][streamer] = round(sum(top_streamers[month][timeslot][streamer]) / len(top_streamers[month][timeslot][streamer]), 2)

        bar.update(i + 1)

    bar.finish()

    # take only the top 10 streamers for each month and timeslot
    for month in top_streamers:
        for timeslot in top_streamers[month]:
            top_streamers[month][timeslot] = {k: v for k, v in sorted(top_streamers[month][timeslot].items(), key=lambda item: item[1], reverse=True)[:10]}

    return top_streamers


def for_handler(years_months, version):
    result_str = ""
    min_total_lives = len(years_months) * 10    # corresponds to 30%

    top_streamers = get_top_streamers_by_viewers_timeslots(years_months, min_total_lives, version)

    # keep only the total
    top_streamers = top_streamers["total"]

    # save the top streamers to csv files
    for timeslot in top_streamers:
        result_str += f"{timeslot}\n"
        for streamer in top_streamers[timeslot]:
            result_str += f"{streamer}\t{top_streamers[timeslot][streamer]}\n"
        result_str += "\n"

    return result_str


def main():
    years_months = ["202404", "202405", "202406"]
    version = "202404-202406"
    min_total_lives = len(years_months) * 10    # corresponds to 30%

    top_streamers = get_top_streamers_by_viewers_timeslots(years_months, min_total_lives, version)

    # save the top streamers to csv files
    for month in top_streamers:
        if month != "total" and month not in years_months:
            continue
        with open(f"analyses_and_data/analysis_results/top_streamers_by_viewers_timeslots-{month}.csv", "w") as file:
            for timeslot in top_streamers[month]:
                file.write(f"{timeslot}\n")
                for streamer in top_streamers[month][timeslot]:
                    file.write(f"{streamer}\t{top_streamers[month][timeslot][streamer]}\n")
                file.write("\n")



if __name__ == "__main__":
    main()
