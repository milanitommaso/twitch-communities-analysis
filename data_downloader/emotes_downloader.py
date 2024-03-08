import requests
import os
import time
import json
from pprint import pprint
from notify_telegram import notify_error as notify_error



def get_channels_to_analyze(n_channels: int):
    # take the top n_channels from top_streamers file

    with open("top_streamers.txt", "r") as f:
        channels_list = f.readlines()[0:n_channels]

    channels_list = [channel.strip() for channel in channels_list]

    return channels_list


def download_global_emotes(past_emotes: dict):
    services = ["twitch", "7tv", "bttv", "ffz"]
    past_emotes = past_emotes.get("global", {})

    emotes_dict = {}    # key: service, value: list of emotes

    for service in services:
        url = "https://emotes.adamcy.pl/v1/global/emotes/" + service

        headers = {"Accept": "application/json"}

        response = requests.get(url, headers=headers)

        emotes = response.json()

        # take only names of emotes
        emotes = [emote["code"] for emote in emotes]

        # union of past emotes and new emotes
        emotes = list(set(past_emotes.get(service, []) + emotes))

        emotes_dict[service] = emotes

        print(f"> Downloaded global emotes for service: {service}")

        time.sleep(1.1)

    return emotes_dict


def download_channel_emotes(channels: list, past_emotes: dict):
    services = ["twitch", "7tv", "bttv", "ffz"]
    emotes_dict = {}    # key: channel, value: dict with key as service and value as list of emotes

    for channel in channels:
        for service in services:
            url = f"https://emotes.adamcy.pl/v1/channel/{channel}/emotes/" + service

            headers = {"Accept": "application/json"}

            try:
                response = requests.get(url, headers=headers)
            except:
                print(f"> Error while making request for channel: {channel}, service: {service}")
                print(response.text)
                continue

            try:
                emotes = response.json()

                # take only names of emotes
                emotes = [emote["code"] for emote in emotes]

                # union of past emotes and new emotes
                emotes = list(set(past_emotes.get(channel, {}).get(service, []) + emotes))

                if channel not in emotes_dict:
                    emotes_dict[channel] = {}

                emotes_dict[channel][service] = emotes

            except:
                print(f"> Error while decoding emotes for channel: {channel}, service: {service}")
                print(response.text)
            else:
                print(f"> Downloaded emotes for channel: {channel}, service: {service}")

            time.sleep(1.1)

    return emotes_dict


def sort_emotes(emotes: dict):
    # sort emotes in each service for each channel
    for channel, emotes_dict in emotes.items():
        for service, emotes_list in emotes_dict.items():
            emotes_list.sort()

    # sort the services for each channel
    for channel, emotes_dict in emotes.items():
        emotes[channel] = dict(sorted(emotes_dict.items()))

    # sort the channels
    emotes = dict(sorted(emotes.items()))

    # put global emotes at the start
    global_emotes = emotes.pop("global")
    emotes = {"global": global_emotes, **emotes}

    return emotes


def main():
    # load downloaded emotes
    if os.path.exists("downloaded_emotes.json"):
        with open("downloaded_emotes.json", "r") as f:
            past_emotes = json.load(f)
    else:
        past_emotes = {}

    global_emotes = download_global_emotes(past_emotes)

    channels_to_analyze = get_channels_to_analyze(n_channels=200)

    emotes = download_channel_emotes(channels_to_analyze, past_emotes)
    emotes = dict(sorted(emotes.items()))

    emotes["global"] = global_emotes

    emotes = sort_emotes(emotes)

    # save emotes to json file
    with open("downloaded_emotes.json", "w") as f:
        json.dump(emotes, f, indent=4)


if __name__ == "__main__":
    print("> Started download emotes")

    while True:
        try:
            main()
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            tg_message = f"Error in streams_info.py\nError decoding response"
            print("> " + tg_message)
            notify_error(tg_message)

        time.sleep(43200)    # every 12 hours
