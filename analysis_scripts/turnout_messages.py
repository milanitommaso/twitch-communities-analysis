import os
import progressbar
from datetime import datetime

MONTHS = ["december", "january", "february", "march"]


def get_days_of_week():
    return ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def get_minutes_of_day():
    minutes = []
    for hour in range(24):
        for minute in range(60):
            minutes.append(f"{str(hour).zfill(2)}-{str(minute).zfill(2)}")
    
    return minutes


def get_turnout():
    turnout = {}

    # get all channels dirs
    channels_dirs = [x for x in os.listdir("downloaded_chats") if "template" not in x]

    bar = progressbar.ProgressBar(maxval=len(channels_dirs), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, channel in enumerate(channels_dirs):
        # get all chat files
        chats = [x for x in os.listdir("downloaded_chats/" + channel) if "template" not in x]

        for chat in chats:

            if datetime.strptime(chat.split("_")[1], "%y-%m-%d").strftime("%B").lower() not in MONTHS:
                continue

            with open("downloaded_chats/" + channel + "/" + chat, "r") as file:
                lines = file.readlines()

            for line in lines:
                dt = line.split("\t")[0].strip()
                if dt == "":
                    continue

                dt = dt[:14]

                if dt not in turnout:
                    turnout[dt] = 0
                turnout[dt] += 1

        bar.update(i + 1)

    bar.finish()

    # get the list of number of messages per day and hour-minute
    days = get_days_of_week()
    minutes = get_minutes_of_day()
    turnout_week = {day: {minute: [] for minute in minutes} for day in days}

    bar = progressbar.ProgressBar(maxval=len(turnout), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    for i, dt in enumerate(turnout):
        day = datetime.strptime(dt, "%y-%m-%d_%H-%M").strftime("%A").lower()
        month = datetime.strptime(dt, "%y-%m-%d_%H-%M").strftime("%B").lower()
        if month not in MONTHS:
            continue

        hour_minute = dt.split("_")[1]
        turnout_week[day][hour_minute].append(turnout[dt])

        bar.update(i + 1)

    bar.finish()

    # calculate the mean viewers day and hour-minute
    for day in turnout_week:
        for minute in turnout_week[day]:
            if len(turnout_week[day][minute]) == 0:
                turnout_week[day][minute] = 0
            else:
                # remove the 0s
                turnout_week[day][minute] = [x for x in turnout_week[day][minute] if x != 0]
                turnout_week[day][minute] = int(sum(turnout_week[day][minute]) / len(turnout_week[day][minute]))


    # for each day, sort the turnout by hour-minute
    for day in turnout_week:
        turnout_week[day] = dict(sorted(turnout_week[day].items()))

    return turnout_week


def main():
    turnout = get_turnout()

    # save the turnout to a csv file
    minutes = get_minutes_of_day()

    with open(f"analysis_results/turnout_messages.csv", "w") as file:
        file.write("Hour:Minute\t")
        days = get_days_of_week()
        for day in days:
            file.write(f"{day}\t")

        file.write("\n")

        for minute in minutes:
            if int(minute.split("-")[1]) % 30 != 0:
                continue

            file.write(f"{minute[:2]}:{minute[3:5]}\t")
            for day in days:
                if minute in turnout[day]:
                    file.write(f"{turnout[day][minute]}\t")
                else:
                    file.write("0\t")
            file.write("\n")

if __name__ == "__main__":
    main()
