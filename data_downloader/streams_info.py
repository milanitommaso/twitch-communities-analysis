import requests, time, datetime, traceback

from config import *
from notify_telegram import notify_error as notify_error


def save_streams_info():
    #make a request to the twitch api to get the list of channels
    url = f"https://api.twitch.tv/helix/streams?language=it&first=100"
    headers = {
        "Authorization": AUTHORIZATION_TWITCH_API,
        "Client-Id": CLIENT_ID
    }

    response = requests.get(url, headers=headers)
    cursor = response.json()["pagination"]["cursor"]

    live_info_list = []
    for live in response.json()["data"]:
        if live["viewer_count"] > 5 and live["user_name"] not in [x["user_name"] for x in live_info_list]:
            live_info_list.append({"user_name": live["user_name"], "category": live["game_name"], "viewer_count": live["viewer_count"]})

    # if there are more streams, make another request
    while cursor is not None:
        url = f"https://api.twitch.tv/helix/streams?language=it&first=100&after={cursor}"
        response = requests.get(url, headers=headers)

        for live in response.json()["data"]:
            if live["viewer_count"] > 5 and live["user_name"] not in [x["user_name"] for x in live_info_list]:
                live_info_list.append({"user_name": live["user_name"], "category": live["game_name"], "viewer_count": live["viewer_count"]})

        if "cursor" not in response.json()["pagination"]:
            break
        cursor = response.json()["pagination"]["cursor"]

    # sort the list by viewer count
    live_info_list.sort(key=lambda x: x["viewer_count"], reverse=True)

    # create a string with the info
    live_info_str = ""
    for live in live_info_list:
        live_info_str += f"{live['user_name']}\t{live['category']}\t{live['viewer_count']}\n"   # use \t instead of spaces because the category can contain spaces

    # save the streams info in a file
    filename = f"streams_info/streams_info{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    with open(filename, "w") as f:
        f.write(live_info_str)
        # print("live info saved")


def main():
    print("> Started saving streams info every minute")
    while True:
        try:
            save_streams_info()
        except KeyboardInterrupt:
            return
        except Exception as e:
            tb = traceback.format_exc()
            print(tb)
            tg_message = f"Error in streams_info.py\n{tb}"
            notify_error(tg_message)

        time.sleep(60)    # every minute

if __name__ == "__main__":
    main()
