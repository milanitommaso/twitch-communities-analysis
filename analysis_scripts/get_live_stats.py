import os
from datetime import datetime, timedelta
import progressbar
import json

def get_current_users_and_lives():
    # Get the current number of users
    current_users = 0
    current_lives = 0

    filename = "streams_info/" + sorted(os.listdir("streams_info"))[-1]

    with open(filename, "r") as f:
        data = f.readlines()
        current_lives = len(data) - 1

    for line in data:
        current_users += int(line.split("\t")[2])

    return current_users, current_lives


def messages_last_hour():
    # Get the number of messages sent in the last hour
    messages_count = 0

    end_datetime = datetime.now()
    start_datetime = end_datetime - timedelta(hours=1)

    # get all the dirs representing the channels
    files = list(os.listdir('downloaded_chats'))
    dirs = [x for x in files if os.path.isdir(os.path.join('downloaded_chats', x))]

    bar = progressbar.ProgressBar(maxval=len(dirs), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    # for each dir, get all the files representing the chats
    for i, d in enumerate(dirs):
        bar.update(i+1)

        files = list(os.listdir(os.path.join('downloaded_chats', d)))

        # for each file, open it and save the chatters in a dict
        for f in files:
            # if the file has been created after the end datetime, skip the file
            if datetime.strptime(f.split('.')[0].replace("chat_", ""), '%y-%m-%d_%H-%M-%S') < end_datetime-timedelta(days=5):
                continue

            with open(os.path.join('downloaded_chats', d, f), 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            # if the timestamp of the last line is before the start datetime, skip the file
            try:
                last_line = lines[-1]
            except:
                continue

            last_ts = last_line.split('\t')[0]
            if datetime.strptime(last_ts, '%y-%m-%d_%H-%M-%S') < start_datetime:
                continue

            j = 0
            while j < len(lines):
                try:
                    # get the timestamp of the message
                    ts = lines[j].split('\t')[0]
                except:
                    j += 1
                    continue

                ts = datetime.strptime(ts, '%y-%m-%d_%H-%M-%S')
                
                if ts < start_datetime:
                    j += 20
                    continue
                elif ts > end_datetime:
                    break
                    
                messages_count += 1
                j += 1

    bar.finish()

    return messages_count


def main():
    print("> getting messages count")
    messages = messages_last_hour()

    print("> getting current users and lives")
    users, lives = get_current_users_and_lives()

    with open("analysis_results/live_stats.json", "w") as f:
        json.dump({"messages_last_hour": messages, "current_users": users, "current_lives": lives}, f, indent=4)


if __name__ == '__main__':
    main()
