import pandas as pd
import os
import json
import progressbar
import sys
import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..', "data_downloader"))
from config import *

TOP_CONTRIBUTORS_PERCENTAGE = 0.01

def get_timestamp_from_filename(filename):
    return datetime.datetime.strptime(filename, "chat_%y-%m-%d_%H-%M-%S.txt")

def get_chats_dataframes_to_analyze(directory: str):
    chats_dataframes = {}   # key: channel name, value: dataframes
    lives = []

    # get all the dirs where there are the chat files
    channel_dirs = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]

    # for every dir get the dataframes of the live streaming chat, a live streaming could have more than one chat file

    # get the lives file
    # for every live streaming get the chat files and concat all the dataframes in one

    with open('lives.txt', 'r') as f:
        lines = f.readlines()

    for l in lines:
        lives.append([l.split('\t')[0], l.split('\t')[1], l.split('\t')[2].strip()])

    bar = progressbar.ProgressBar(maxval=len(channel_dirs), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, d in enumerate(channel_dirs):
        channel_files = os.listdir(os.path.join(directory, d))

        # get the lives of the channel
        channel_lives = [l for l in lives if l[0] == d]

        lives_to_analyze = []   # list of list of lives to analyze, every internal list contains all the filenames of the lives to analyze, the external list contains all the lives
        for c_l in channel_lives:
            live_chats = []
            for c in channel_files:
                if get_timestamp_from_filename(c) >= datetime.datetime.strptime(c_l[1], "%Y-%m-%d %H:%M:%S") and get_timestamp_from_filename(c) <= datetime.datetime.strptime(c_l[2], "%Y-%m-%d %H:%M:%S"):
                    live_chats.append(c)
            lives_to_analyze.append(live_chats)


        # for every live get the chat files and concat all the dataframes in one
        live_df = pd.DataFrame(columns=['timestamp', 'is_mod', 'is_sub', 'user', 'message'])
        for live in lives_to_analyze:
            for c in live:
                live_df = pd.concat([live_df, get_dataframe_from_chat_file(os.path.join(directory, d, c))])

        if d not in chats_dataframes:
            chats_dataframes[d] = []
        chats_dataframes[d].append(live_df)

        bar.update(i + 1)

    bar.finish()

    return chats_dataframes


def get_dataframe_from_chat_file(chat_filename):
    # create a dataframe with columns: timestamp, is_mod, is_sub, message
    chat_df = pd.DataFrame(columns=['timestamp', 'is_mod', 'is_sub', 'user', 'message'])

    # read the csv file
    try:
        chat_df = pd.read_csv(chat_filename, sep='\t', names=['timestamp', 'is_mod', 'is_sub', 'user', 'message'])
    except:
        print("Error reading file: ", chat_filename)
        return chat_df

    # delete the rows where the user is in the bot list
    chat_df = chat_df[~chat_df['user'].isin(KNOWN_BOTS)]

    # take only the user column
    chat_df = chat_df[['user']]

    return chat_df


def get_top_contributors(chat_df):
    # get the total number of messages
    total_messages = chat_df.shape[0]

    # get the number of messages sent by each user
    user_messages = chat_df['user'].value_counts()

    # sort the users by number of messages
    user_messages.sort_values(ascending=False, inplace=True)

    # get the number of messages of the last user

    # take the first TOP_CONTRIBUTORS_PERCENTAGE of the users
    top_contributors_messages = user_messages.head(int(total_messages * TOP_CONTRIBUTORS_PERCENTAGE))

    # get the top contributors
    top_contributors = top_contributors_messages.index.tolist()

    return top_contributors


def get_top_contributors_impact(chat_df, top_contributors):
    # get the total number of messages
    total_messages = chat_df.shape[0]
    if total_messages == 0:
        return 0

    # get the number of messages sent by top contributors
    top_contributors_messages_count = chat_df[chat_df['user'].isin(top_contributors)].shape[0]

    # get the impact of the top contributors
    impact = top_contributors_messages_count / total_messages

    return impact


if __name__ == "__main__":
    saved_impacts = {}
    chats_dataframes = {}   # key: channel name, value: dataframes

    print("> Reading chat files and converting them to dataframes...")
    chats_dataframes = get_chats_dataframes_to_analyze("downloaded_chats")

    print("> Analyzing chat files...")
    bar = progressbar.ProgressBar(maxval=len(chats_dataframes), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, (channel_name, dataframes) in enumerate(chats_dataframes.items()):
        # get the channel name from the filename

        for df in dataframes:
            top_contributors = get_top_contributors(df)

            impact = get_top_contributors_impact(df, top_contributors)

            if channel_name not in saved_impacts:
                saved_impacts[channel_name] = []
            saved_impacts[channel_name].append(impact)
        
        bar.update(i + 1)

    bar.finish()

    # get the total impact
    sum_impact = 0
    count = 0

    for channel_name in saved_impacts:
        if sum(saved_impacts[channel_name]) != 0:
            sum_impact += sum(saved_impacts[channel_name])
            count += len(saved_impacts[channel_name])

    saved_impacts['total'] = '%.2f'%((sum_impact / count) * 100)

    # get the average impact for every channel
    for channel_name in saved_impacts:
        if channel_name == 'total':
            continue
        saved_impacts[channel_name] = '%.2f'%((sum(saved_impacts[channel_name]) / len(saved_impacts[channel_name])) * 100)

    # sort the channels by name
    saved_impacts = {k: v for k, v in sorted(saved_impacts.items(), key=lambda item: item[0])}

    # move the total impact to the start
    saved_impacts = {'total': saved_impacts['total'], **saved_impacts}

    print(saved_impacts)

    # save the impacts in json
    with open('top_contributors_impact.json', 'w') as f:
        json.dump(saved_impacts, f, indent=4)
