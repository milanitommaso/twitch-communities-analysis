from pprint import pprint


def get_days_of_week():
    return ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def get_minutes_of_day():
    minutes = []
    for hour in range(24):
        for minute in range(60):
            minutes.append(f"{str(hour).zfill(2)}:{str(minute).zfill(2)}")
    
    return minutes


def get_turnout_messages_viewers():
    # open the turnout.csv file and create a dictionary
    viewers_dict = {}   # key: day, value: dict with key: hour-minute, value: number of viewers

    with open("analysis_results/turnout-total.csv", "r") as file:
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

    with open("analysis_results/turnout_messages.csv", "r") as file:
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


def main():

    messages_viewers_dict = get_turnout_messages_viewers()

    # save the turnout to a csv file
    minutes = get_minutes_of_day()
    days = get_days_of_week()

    with open(f"analysis_results/turnout_messages_viewers.csv", "w") as file:
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
