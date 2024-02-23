import os
import json
import progressbar
from datetime import datetime, timedelta, time

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


def get_days_timeslots_from_range(start, end) -> tuple[list, list]:
    day_timeslot_list = []

    if start >= end:
        print("Error: start time is greater than or equal to end time")
        return

    while start <= end:
        day = start.strftime("%A").lower()
        timeslot = get_timeslot(start.time())

        # if the timeslot is evening and the start time is after midnight, then the day is the previous day
        if timeslot == "evening" and start.time() >= time(0, 0, 0) and start.time() <= time(1, 0, 0):
            day = (start - timedelta(days=1)).strftime("%A").lower()

        day_timeslot_list.append([day, timeslot])

        start += timedelta(minutes=30)
    
    # get all the unique days and timeslots
    new_day_timeslot_list = []
    for elem in day_timeslot_list:
        if elem not in new_day_timeslot_list:
            new_day_timeslot_list.append(elem)
    day_timeslot_list = new_day_timeslot_list

    return day_timeslot_list


def get_lives_count() -> dict:
    # get lives count for each streamer for each timeslot
    lives = {}

    with open("lives.txt", "r") as file:
        lines = file.readlines()

    print("> Calculating lives count for each streamer for each timeslot")
    bar = progressbar.ProgressBar(maxval=len(lines), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, line in enumerate(lines):
        channel = line.split("\t")[0].strip()
        timestamp_start = line.split("\t")[1].strip()
        timestamp_end = line.split("\t")[2].strip()

        datetime_start = datetime.strptime(timestamp_start, "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.strptime(timestamp_end, "%Y-%m-%d %H:%M:%S")

        day_timeslot_list = get_days_timeslots_from_range(datetime_start, datetime_end)

        for day, timeslot in day_timeslot_list:
            if day not in lives:
                lives[day] = {"morning": {}, "afternoon": {}, "evening": {}, "night": {}}
            if timeslot not in lives[day]:
                lives[day][timeslot] = {}

            if channel not in lives[day][timeslot]:
                lives[day][timeslot][channel] = 0
            lives[day][timeslot][channel] += 1
        
        bar.update(i + 1)

    bar.finish()

    # for every day and timeslot, sort the streamers by lives count
    for day in lives:
        for timeslot in lives[day]:
            lives[day][timeslot] = {k: v for k, v in sorted(lives[day][timeslot].items(), key=lambda item: item[1], reverse=True)}

    return lives


def get_top_streamers_by_viewers_timeslots():
    top_streamers = {}
    # top_streamers = {
    #   "monday": {
    #       "morning": {"streamer1":[1000, 1150], "streamer2":[900, 765, 945], ...},
    #       "afternoon": {...},
    #       "evening": {...},
    #       "night": {...}
    #   },
    #   "tuesday": {...},
    #   ...
    # }

    lives_count = get_lives_count()

    # get all streams info filenames
    streams_info = [x for x in os.listdir("streams_info") if "template" not in x]
    streams_info.sort()

    streams_info = streams_info[::5]  # take every 5th file to reduce the number of files to process

    print("> Calculating top streamers by viewers for each timeslot")
    bar = progressbar.ProgressBar(maxval=len(streams_info), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, streams in enumerate(streams_info):
        datetime = get_datetime_from_streams_info_filename(streams)
        time = datetime.time()
        day = datetime.strftime("%A").lower()
        timeslot = get_timeslot(time)

        if day not in top_streamers:
            top_streamers[day] = {"morning": {}, "afternoon": {}, "evening": {}, "night": {}}

        with open("streams_info/" + streams, "r") as file:
            lines = file.readlines()

        for line in lines:
            streamer = line.split("\t")[0].strip()
            viewers = int(line.split("\t")[2].strip())

            if streamer not in top_streamers[day][timeslot]:
                top_streamers[day][timeslot][streamer] = []
            top_streamers[day][timeslot][streamer].append(viewers)

        bar.update(i + 1)

    bar.finish()
    

    print("> Calculating average viewers for each streamer for each timeslot")
    bar = progressbar.ProgressBar(maxval=len(top_streamers), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    # calculate the average viewers for each streamer
    for i, day in enumerate(top_streamers):
        for timeslot in top_streamers[day]:
            for streamer in top_streamers[day][timeslot]:
                # check if the streamer has at least 5 lives in the timeslot and day
                if streamer not in lives_count[day][timeslot] or lives_count[day][timeslot][streamer] < 5:
                    top_streamers[day][timeslot][streamer] = -1
                    continue
                top_streamers[day][timeslot][streamer] = round(sum(top_streamers[day][timeslot][streamer]) / len(top_streamers[day][timeslot][streamer]), 2)

        bar.update(i + 1)

    bar.finish()

    # take only the top 50 streamers for each timeslot and day
    for day in top_streamers:
        for timeslot in top_streamers[day]:
            top_streamers[day][timeslot] = {k: v for k, v in sorted(top_streamers[day][timeslot].items(), key=lambda item: item[1], reverse=True)}
            top_streamers[day][timeslot] = dict(list(top_streamers[day][timeslot].items())[:50])

    # for every day and timeslot, sort the streamers by average viewers
    for day in top_streamers:
        for timeslot in top_streamers[day]:
            top_streamers[day][timeslot] = {k: v for k, v in sorted(top_streamers[day][timeslot].items(), key=lambda item: item[1], reverse=True)}

    return top_streamers


def main():
    top_streamers = get_top_streamers_by_viewers_timeslots()

    # save the top streamers to a json file
    with open("analysis_results/top_streamers_by_viewers_timeslot.json", "w") as file:
        json.dump(top_streamers, file, indent=4)


if __name__ == "__main__":
    main()

    # x = get_days_timeslots_from_range(datetime.strptime("2023-12-01 14:00:00", "%Y-%m-%d %H:%M:%S"), datetime.strptime("2023-12-05 09:00:00", "%Y-%m-%d %H:%M:%S"))
    # print(x)
