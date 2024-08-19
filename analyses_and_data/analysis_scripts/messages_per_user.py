ANALYSES_REQUIRED = ["turnout", "turnout_by_messages"]


def get_days_of_week():
    return ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def get_minutes_of_day():
    minutes = []
    for hour in range(24):
        for minute in range(60):
            minutes.append(f"{str(hour).zfill(2)}:{str(minute).zfill(2)}")
    
    return minutes


def get_turnout_messages_viewers(version):
    # open the turnout.csv file and create a dictionary
    viewers_dict = {}   # key: day, value: dict with key: hour-minute, value: number of viewers

    with open(f"website/static/analyses_results/turnout/{version}.csv", "r") as file:
        lines = file.readlines()
    for i, line in enumerate(lines):
        if i == 0:
            days = line.strip().split("\t")[1:]
            continue

        hour_minute = line.strip().split("\t")[0]

        for j, day in enumerate(days):
            if day not in viewers_dict:
                viewers_dict[day] = {}
            viewers_dict[day][hour_minute] = line.strip().split("\t")[j + 1]


    # open the turnout_messages.csv file and create a dictionary
    messages_dict = {}   # key: day, value: dict with key: hour-minute, value: number of messages

    with open(f"website/static/analyses_results/turnout-by-messages/{version}.csv", "r") as file:
        lines = file.readlines()
    for i, line in enumerate(lines):
        if i == 0:
            days = line.strip().split("\t")[1:]
            continue

        hour_minute = line.strip().split("\t")[0]

        for j, day in enumerate(days):
            if day not in messages_dict:
                messages_dict[day] = {}
            messages_dict[day][hour_minute] = line.strip().split("\t")[j + 1]

    # create a dict with the number of messages / viewers
    messages_viewers_dict = {}  # key: day, value: dict with key: hour-minute, value: number of messages / viewers
    for day in viewers_dict:
        for hour_minute in viewers_dict[day]:
            if day not in messages_viewers_dict:
                messages_viewers_dict[day] = {}
            if hour_minute not in messages_viewers_dict[day]:
                messages_viewers_dict[day][hour_minute] = 0

            messages_viewers_dict[day][hour_minute] = float(messages_dict[day][hour_minute]) / float(viewers_dict[day][hour_minute])

    return messages_viewers_dict


def for_handler(version):
    messages_viewers_dict = get_turnout_messages_viewers(version)

    # save the turnout to a csv file
    minutes = get_minutes_of_day()
    days = get_days_of_week()

    result_str = ""

    result_str += "Hour:Minute\t"
    for day in days:
        result_str += f"{day}\t"

    result_str += "\n"

    for minute in minutes:
        if int(minute.split(":")[1]) % 30 != 0:
            continue
        
        result_str += f"{minute[:2]}:{minute[3:5]}\t"
        for day in days:
            if minute in messages_viewers_dict[day]:
                result_str += f"{messages_viewers_dict[day][minute]}\t"
            else:
                result_str += "0\t"
        result_str += "\n"

    return result_str


def main():
    version = "202404-202406"
    messages_viewers_dict = get_turnout_messages_viewers(version)

    # save the turnout to a csv file
    minutes = get_minutes_of_day()
    days = get_days_of_week()

    with open(f"analyses_and_data/analysis_results/turnout_messages_viewers.csv", "w") as file:
        file.write("Hour:Minute\t")
        for day in days:
            file.write(f"{day}\t")

        file.write("\n")

        for minute in minutes:
            if int(minute.split(":")[1]) % 30 != 0:
                continue
            
            file.write(f"{minute[:2]}:{minute[3:5]}\t")
            for day in days:
                if minute in messages_viewers_dict[day]:
                    file.write(f"{messages_viewers_dict[day][minute]}\t")
                else:
                    file.write("0\t")
            file.write("\n")


if __name__ == "__main__":
    main()
