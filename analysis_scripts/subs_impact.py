import pandas as pd
import os
import progressbar
import sys
import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..', "data_downloader"))
from config import *

MONTHS = ["december","january","february","march"]


def get_top_streamers(number_of_streamers):
    top_streamers = []

    with open('top_streamers.txt', 'r') as f:
        lines = f.readlines()[0:number_of_streamers]

    for l in lines:
        top_streamers.append(l.strip())

    return top_streamers


def get_timestamp_from_filename(filename):
    return datetime.datetime.strptime(filename, "chat_%y-%m-%d_%H-%M-%S.txt")


def get_chats_dataframes_to_analyze(directory: str):
    chats_dataframes = {}   # key: channel name, value: dataframes
    lives = []

    # get the 60 top streamers, because we can't analyze all the streamers
    top_streamers = get_top_streamers(number_of_streamers=60)

    # get all the dirs where there are the chat files
    channel_dirs = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]

    # take only the dirs of the top streamers
    channel_dirs = [d for d in channel_dirs if d in top_streamers]

    # for every dir get the dataframes of the live streaming chat, a live streaming could have more than one chat file

    # get the lives file
    # for every live streaming get the chat files and concat all the dataframes in one

    with open('lives.txt', 'r') as f:
        lines = f.readlines()

    for l in lines:
        # check that the end of the live is in a month in MONTHS
        if datetime.datetime.strptime(l.split('\t')[2].split(' ')[0], "%Y-%m-%d").strftime('%B').lower() in MONTHS:
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
        live_df = pd.DataFrame(columns=['is_sub', 'user'])
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
        # print("Error reading file: ", chat_filename)
        return chat_df

    # delete the rows where the user is in the bot list
    chat_df = chat_df[~chat_df['user'].isin(KNOWN_BOTS)]

    # take only the user column
    chat_df = chat_df[['is_sub', 'user']]

    return chat_df


def get_subscribers_messages_count(df):
    # get the number of messages sent by subscribers
    # filter the dataframe by the subscribers
    df = df[df['is_sub'] == 1]

    # get the number of messages sent by subscribers
    subscribers_messages_count = df.shape[0]

    return subscribers_messages_count


def get_subscribers_impact(df, subscribers_messages_count):
    # get the total number of messages
    total_messages = df.shape[0]
    if total_messages == 0:
        return 0

    # get the impact of the top contributors
    impact = subscribers_messages_count / total_messages

    return impact


def get_total_impact(saved_impacts):
    top_streamers = get_top_streamers(number_of_streamers=50)

    # get the impact for every channel
    for channel_name in saved_impacts:
        if channel_name == 'total':
            continue
        saved_impacts[channel_name] = round(((sum(saved_impacts[channel_name]) / len(saved_impacts[channel_name])) * 100), 2)
    
    # get the average impact
    sum_impact = 0
    count = 0
    for channel_name in saved_impacts:
        if saved_impacts[channel_name] != 0:
            sum_impact += saved_impacts[channel_name]
            count += 1

    saved_impacts['total'] = round((sum_impact / count), 2)

    # get the average impact only for top 50 streamers
    sum_impact = 0
    count = 0
    for channel_name in saved_impacts:
        if saved_impacts[channel_name] != 0 and channel_name in top_streamers:
            sum_impact += saved_impacts[channel_name]
            count += 1

    saved_impacts['total_top_streamers'] = round((sum_impact / count), 2)

    # sort the channels by name
    saved_impacts = {k: v for k, v in sorted(saved_impacts.items(), key=lambda item: item[0])}

    # move the totals impact to the start
    saved_impacts = {'total': saved_impacts['total'], **saved_impacts}
    saved_impacts = {'total_top_streamers': saved_impacts['total_top_streamers'], **saved_impacts}

    return saved_impacts


def main():
    saved_impacts = {}
    chats_dataframes = {}   # key: channel name, value: dataframes

    print("> Reading chat files and converting them to dataframes...")
    chats_dataframes = get_chats_dataframes_to_analyze("downloaded_chats")

    print("> Analyzing chat files...")
    bar = progressbar.ProgressBar(maxval=len(chats_dataframes), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, (channel_name, dataframes) in enumerate(chats_dataframes.items()):
        for df in dataframes:
            subscribers_messages_count = get_subscribers_messages_count(df)

            impact = get_subscribers_impact(df, subscribers_messages_count)

            if channel_name not in saved_impacts:
                saved_impacts[channel_name] = []
            saved_impacts[channel_name].append(impact)
        
        bar.update(i + 1)

    bar.finish()

    saved_impacts = get_total_impact(saved_impacts)

    # save the impacts in a csv file, only for top 60 streamers
    top_streamers = get_top_streamers(number_of_streamers=60)
    with open('analysis_results/subscribers_impact.csv', 'w') as f:
        f.write("channel\timpact\n")
        f.write(f"total\t{saved_impacts['total']}\n")
        f.write(f"total_top_streamers\t{saved_impacts['total_top_streamers']}\n")
        for channel_name in top_streamers:
            f.write(f"{channel_name}\t{saved_impacts[channel_name]}\n")


if __name__ == "__main__":
    main()
