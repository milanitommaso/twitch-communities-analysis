import os
import datetime
import progressbar

def get_messages_last_hour():
    chatters_last_hour = 0
    print("Getting messages from the last hour")

    files = list(os.listdir('analyses_and_data/downloaded_chats'))
    dirs = [x for x in files if os.path.isdir(os.path.join('analyses_and_data/downloaded_chats', x))]

    start_datetime = datetime.datetime.now() - datetime.timedelta(hours=1)
    end_datetime = datetime.datetime.now()

    bar = progressbar.ProgressBar(maxval=len(dirs), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, d in enumerate(dirs):
        bar.update(i)

        files = list(os.listdir(os.path.join('analyses_and_data/downloaded_chats', d)))

        # take only the last 3 files for directory, ordered by creation date
        files.sort(key=lambda x: os.path.getctime(os.path.join('analyses_and_data/downloaded_chats', d, x)), reverse=True)
        files = files[:3]


        # for each file, open it and save the chatters in a dict
        for f in files:
            # if the file has been created after the end datetime, skip the file
            if datetime.datetime.strptime(f.split('.')[0].replace("chat_", ""), '%y-%m-%d_%H-%M-%S') > end_datetime:
                continue

            with open(os.path.join('analyses_and_data/downloaded_chats', d, f), 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            # if the timestamp of the last line is before the start datetime, skip the file
            try:
                last_line = lines[-1]
            except:
                continue

            last_ts = last_line.split('\t')[0]
            if datetime.datetime.strptime(last_ts, '%y-%m-%d_%H-%M-%S') < start_datetime:
                continue

            j = 0
            while j < len(lines):
                try:
                    # get the timestamp of the message
                    ts = lines[j].split('\t')[0]
                except:
                    j += 1
                    continue

                ts = datetime.datetime.strptime(ts, '%y-%m-%d_%H-%M-%S')
                
                if ts < start_datetime:
                    j += 50
                    continue
                elif ts > end_datetime:
                    break
            
                chatters_last_hour += 1

                j += 1

    bar.finish()

    return chatters_last_hour


def get_current_users():
    lives = [f for f in os.listdir('analyses_and_data/streams_info') if not f.startswith('.') and 'template' not in f.lower()]
    lives.sort()

    # get number of lines in the last file
    with open(f'analyses_and_data/streams_info/{lives[-1]}', 'r') as f:
        lines = f.readlines()

    users = 0
    for line in lines:
        users += int(line.split('\t')[2])

    return users


def get_current_lives():
    lives = [f for f in os.listdir('analyses_and_data/streams_info') if not f.startswith('.') and 'template' not in f.lower()]
    lives.sort()

    # get number of lines in the last file
    with open(f'analyses_and_data/streams_info/{lives[-1]}', 'r') as f:
        lines = f.readlines()

    return len(lines)


def for_handler():
    return {
        'messages_last_hour': get_messages_last_hour(),
        'current_users': get_current_users(),
        'current_lives': get_current_lives()
    }
