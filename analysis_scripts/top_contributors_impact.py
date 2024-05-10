import pandas as pd
import os
import progressbar
import sys
import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..', "data_downloader"))
from config import *

MONTHS = ["december","january","february","march"]
TOP_N_CHATTERS = [10, 50, 100]


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
        live_df = pd.DataFrame(columns=['user'])
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
    chat_df = chat_df[['user']]

    return chat_df


def get_top_contributors(chat_df, top_n_contributors: int):
    # get the number of messages sent by each user
    user_messages = chat_df['user'].value_counts()

    # sort the users by number of messages
    user_messages.sort_values(ascending=False, inplace=True)

    # take the messages of the top_n_contributors
    top_contributors_messages = user_messages.head(top_n_contributors)

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
    impact = (top_contributors_messages_count / total_messages) * 100

    return impact


def get_total_impact(saved_impacts):
    # saved_impacts = {channel_name: {top10: [impact1, impact2, ...], top50:[impact3, impact4]}, ...}

    for channel_name in saved_impacts:
        for top_n in saved_impacts[channel_name]:
            saved_impacts[channel_name][top_n] = sum(saved_impacts[channel_name][top_n]) / len(saved_impacts[channel_name][top_n])
            # use only 2 decimal places
            saved_impacts[channel_name][top_n] = round(saved_impacts[channel_name][top_n], 2)

    # get the average impact
    average_impacts = {}
    for channel_name in saved_impacts:
        for top_n in saved_impacts[channel_name]:
            if top_n not in average_impacts:
                average_impacts[top_n] = []
            average_impacts[top_n].append(saved_impacts[channel_name][top_n])

    for top_n in average_impacts:
        average_impacts[top_n] = sum(average_impacts[top_n]) / len(average_impacts[top_n])
        average_impacts[top_n] = round(average_impacts[top_n], 2)

    saved_impacts['total'] = average_impacts

    # get the average impact only for top 50 streamers
    top_50_streamers = get_top_streamers(number_of_streamers=50)
    average_impacts_top_streamers = {}
    for channel_name in saved_impacts:
        if channel_name not in top_50_streamers:
            continue

        for top_n in saved_impacts[channel_name]:
            if top_n not in average_impacts_top_streamers:
                average_impacts_top_streamers[top_n] = []
            average_impacts_top_streamers[top_n].append(saved_impacts[channel_name][top_n])

    for top_n in average_impacts_top_streamers:
        average_impacts_top_streamers[top_n] = sum(average_impacts_top_streamers[top_n]) / len(average_impacts_top_streamers[top_n])
        average_impacts_top_streamers[top_n] = round(average_impacts_top_streamers[top_n], 2)

    saved_impacts['total_top_streamers'] = average_impacts_top_streamers

    # order the dictionary using the order of top streamers
    top_60_streamers = get_top_streamers(number_of_streamers=60)
    saved_impacts_ordered = {}
    for streamer in top_60_streamers:
        if streamer in saved_impacts:
            saved_impacts_ordered[streamer] = saved_impacts[streamer]

    # move the totals impact to the start
    saved_impacts_ordered = {'total': saved_impacts['total'], **saved_impacts_ordered}
    saved_impacts_ordered = {'total_top_streamers': saved_impacts['total_top_streamers'], **saved_impacts_ordered}

    return saved_impacts_ordered


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
            for top_n in TOP_N_CHATTERS:
                top_n_str = "top" + str(top_n)

                top_n_contributors = get_top_contributors(df, top_n)

                if len(top_n_contributors) != top_n:
                    continue

                impact = get_top_contributors_impact(df, top_n_contributors)

                if channel_name not in saved_impacts:
                    saved_impacts[channel_name] = {}
                if top_n_str not in saved_impacts[channel_name]:
                    saved_impacts[channel_name][top_n_str] = []

                saved_impacts[channel_name][top_n_str].append(impact)
                
        bar.update(i + 1)

    bar.finish()
    
    saved_impacts = get_total_impact(saved_impacts)

    # save the impacts in a csv file
    with open('analysis_results/top_contributors_impact.csv', 'w') as file:
        file.write("channel_name\ttop10\ttop50\ttop100\n")

        for i, channel_name in enumerate(saved_impacts):
            file.write(channel_name)
            for top_n in saved_impacts[channel_name]:
                file.write("\t" + str(saved_impacts[channel_name][top_n]))
            file.write("\n")


if __name__ == "__main__":
    main()
