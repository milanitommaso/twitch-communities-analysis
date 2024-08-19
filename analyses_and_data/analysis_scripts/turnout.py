import os
import progressbar
from datetime import datetime

ANALYSES_REQUIRED = []


def get_days_of_week():
    return ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def get_year_month_from_streams_info_filename(filename):
    dt =  datetime.strptime(filename, "streams_info%Y-%m-%d_%H-%M-%S.txt")
    return dt.strftime("%Y%m")


def get_day_from_streams_info_filename(filename):
    dt =  datetime.strptime(filename, "streams_info%Y-%m-%d_%H-%M-%S.txt")
    return dt.strftime("%A").lower()


def get_month_from_streams_info_filename(filename):
    dt =  datetime.strptime(filename, "streams_info%Y-%m-%d_%H-%M-%S.txt")
    return dt.strftime("%B").lower()


def get_minute_from_streams_info_filename(filename):
    dt =  datetime.strptime(filename, "streams_info%Y-%m-%d_%H-%M-%S.txt")
    return dt.strftime("%H:%M")


def get_turnout(years_months):
    turnout = {}    # key: day of week, value: dict with key: hour-minute of day, value: list of viewers, than calculate the mean

    # get all streams info filenames
    streams_info = [x for x in os.listdir("analyses_and_data/streams_info") if "template" not in x]
    streams_info.sort()

    bar = progressbar.ProgressBar(maxval=len(streams_info), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, streams in enumerate(streams_info):
        count_viewers = 0
        day = get_day_from_streams_info_filename(streams)
        month = get_month_from_streams_info_filename(streams)

        year_month = get_year_month_from_streams_info_filename(streams)

        if year_month not in years_months:
            bar.update(i + 1)
            continue

        with open("analyses_and_data/streams_info/" + streams, "r") as file:
            lines = file.readlines()
        for line in lines:
            count_viewers += int(line.split("\t")[2].strip())

        if month not in turnout:
            turnout[month] = {}

        if day not in turnout[month]:
            turnout[month][day] = {}

        minute = get_minute_from_streams_info_filename(streams)
        if minute not in turnout[month][day]:
            turnout[month][day][minute] = []
        turnout[month][day][minute].append(count_viewers)

        bar.update(i + 1)

    bar.finish()

    # calculate the mean for all months 
    turnout["total"] = {}
    for month in turnout:
        if month == "total":
            continue
        for day in turnout[month]:
            for minute in turnout[month][day]:
                if day not in turnout["total"]:
                    turnout["total"][day] = {}
                if minute not in turnout["total"][day]:
                    turnout["total"][day][minute] = []
                turnout["total"][day][minute].extend(turnout[month][day][minute])

    # calculate the mean viewers for each month, day and hour-minute
    for month in turnout:
        for day in turnout[month]:
            for minute in turnout[month][day]:
                turnout[month][day][minute] = int(sum(turnout[month][day][minute]) / len(turnout[month][day][minute]))

    # sort the turnout by month
    turnout = dict(sorted(turnout.items()))

    # move total to the start
    total = turnout.pop("total")
    turnout = {"total": total, **turnout}

    # for each month, sort the turnout by day
    for month in turnout:
        turnout[month] = dict(sorted(turnout[month].items()))

    # for each day, sort the turnout by hour-minute
    for month in turnout:
        for day in turnout[month]:
            turnout[month][day] = dict(sorted(turnout[month][day].items()))

    return turnout


def draw_graph(turnout):
    import matplotlib.pyplot as plt

    # make a line for each day
    for day in turnout:
        minutes = list(turnout[day].keys())
        viewers = list(turnout[day].values())
        plt.plot(minutes, viewers, label=day)

    plt.xlabel("Hour-Minute")
    plt.ylabel("Viewers")

    plt.legend()

    # plt.savefig("analysis_results/turnout.png")


def for_handler(years_months: list):
    turnout = get_turnout(years_months)
    
    result_str = ""

    result_str += "Hour:Minute\t"
    days = get_days_of_week()
    for day in days:
        result_str += f"{day}\t"

    result_str += "\n"

    for minute in turnout["total"]["monday"]:
        if int(minute.split(":")[1]) % 30 != 0:
            continue

        result_str += f"{minute}\t"
        for day in days:
            result_str += f"{turnout['total'][day][minute]}\t"
        result_str += "\n"

    return result_str


def main():
    years_months = ["202401", "202402", "202403"]
    turnout = get_turnout(years_months)

    # draw_graph(turnout)

    # save the turnout to a csv file
    for month in turnout:
        with open(f"analyses_and_data/analysis_results/turnout-{month}.csv", "w") as file:
            file.write("Hour:Minute\t")
            days = get_days_of_week()
            for day in days:
                file.write(f"{day}\t")

            file.write("\n")

            for minute in turnout[month]["monday"]:
                if int(minute.split(":")[1]) % 30 != 0:
                    continue

                file.write(f"{minute}\t")
                for day in days:
                    file.write(f"{turnout[month][day][minute]}\t")
                file.write("\n")


if __name__ == "__main__":
    main()
