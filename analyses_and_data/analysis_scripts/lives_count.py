import json
import progressbar
from datetime import datetime, timedelta

START_MORNING_TIMESLOT_STR = "07:00:00"
END_MORNING_TIMESLOT_STR = "12:59:59"
START_AFTERNOON_TIMESLOT_STR = "13:00:00"
END_AFTERNOON_TIMESLOT_STR = "18:59:59"
START_EVENING_TIMESLOT_STR = "19:00:00"
END_EVENING_TIMESLOT_STR = "00:59:59"
START_NIGHT_TIMESLOT_STR = "01:00:00"
END_NIGHT_TIMESLOT_STR = "06:59:59"

ANALYSES_REQUIRED = ["lives"]

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


def get_lives_count(years_months, version) -> dict:
    # get lives count for each streamer for each timeslot
    lives = {}

    with open(f"analyses_and_data/cached_data/lives{version}.txt", "r") as file:
        lines = file.readlines()

    print("> Calculating lives count for each streamer for each timeslot")
    bar = progressbar.ProgressBar(maxval=len(lines), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, line in enumerate(lines):
        bar.update(i + 1)

        channel = line.split("\t")[0].strip()
        timestamp_start = line.split("\t")[1].strip()
        timestamp_end = line.split("\t")[2].strip()

        datetime_start = datetime.strptime(timestamp_start, "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.strptime(timestamp_end, "%Y-%m-%d %H:%M:%S")

        timeslot_list = get_timeslots_from_range(datetime_start, datetime_end)
        month = datetime_start.strftime("%Y%m")

        if month not in years_months:
            continue

        for timeslot in timeslot_list:
            if timeslot not in lives:
                lives[timeslot] = {}

            if channel not in lives[timeslot]:
                lives[timeslot][channel] = 0
            lives[timeslot][channel] += 1 
        
    bar.finish()

    # for every timeslot, sort the streamers by lives count
    for timeslot in lives:
        lives[timeslot] = {k: v for k, v in sorted(lives[timeslot].items(), key=lambda item: item[1], reverse=True)}

    return lives


def for_handler(months, version):
    return get_lives_count(months, version)


def main():
    years_months = ["202404", "202405", "202406"]
    version = "202404-202406"

    result = get_lives_count(years_months, version)

    # save the result to a json file
    with open(f"analyses_and_data/analysis_script/lives_count{version}.json", "w") as file:
        json.dump(result, file, indent=4)


if __name__ == "__main__":
    main()
