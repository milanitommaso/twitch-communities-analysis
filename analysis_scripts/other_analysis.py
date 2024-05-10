import os
import progressbar
import json


def get_total_messages_count():
    total_messages = 0

    channels_dirs = [x for x in os.listdir("downloaded_chats") if "template" not in x]

    print("> Counting total messages")

    bar = progressbar.ProgressBar(maxval=len(channels_dirs), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, channel in enumerate(channels_dirs):
        chats_filenames = os.listdir(f'downloaded_chats/{channel}')
        chats_filenames = [filename for filename in chats_filenames if "template" not in filename]

        for chat_filename in chats_filenames:
            with open(f'downloaded_chats/{channel}/{chat_filename}', 'r') as f:
                lines = f.readlines()

            total_messages += len(lines)

        bar.update(i + 1)

    bar.finish()

    with open("analysis_results/other_analysis.json", "r") as f:
        other_analysis = json.load(f)

    # save the total messages count in the other analysis file
    with open("analysis_results/other_analysis.json", "w") as f:
        other_analysis["total_messages"] = total_messages
        json.dump(other_analysis, f, indent=4)

    return total_messages


def get_unique_chatters_count(): 
    chatters_set = set()

    chatters_filenames = [x for x in os.listdir("chatters") if "template" not in x]

    print("> Counting unique chatters")

    bar = progressbar.ProgressBar(maxval=len(chatters_filenames), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, filename in enumerate(chatters_filenames):
        with open(f'chatters/{filename}', 'r') as f:
            chatters = json.load(f)

        for channel in chatters:
            chatters_set.update(chatters[channel])

        bar.update(i + 1)

    bar.finish()

    with open("analysis_results/other_analysis.json", "r") as f:
        other_analysis = json.load(f)

    # save the total messages count in the other analysis file
    with open("analysis_results/other_analysis.json", "w") as f:
        other_analysis["cahtters_count"] = len(chatters_set)
        json.dump(other_analysis, f, indent=4)

    return len(chatters_set)


def get_unique_streamers_count():
    streamers = [x for x in os.listdir("downloaded_chats") if "template" not in x]

    with open("analysis_results/other_analysis.json", "r") as f:
        other_analysis = json.load(f)

    # save the total messages count in the other analysis file
    with open("analysis_results/other_analysis.json", "w") as f:
        other_analysis["streamers_count"] = len(streamers)
        json.dump(other_analysis, f, indent=4)

    return len(streamers)


def main():
    total_messages_count = get_total_messages_count()
    print(total_messages_count)

    unique_chatters_count = get_unique_chatters_count()
    print(unique_chatters_count)

    unique_streamers_count = get_unique_streamers_count()
    print(unique_streamers_count)



if __name__ == "__main__":
    main()
