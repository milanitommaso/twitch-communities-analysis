import os
from pprint import pprint
from datetime import datetime, timedelta
import progressbar
import matplotlib.pyplot as plt
import numpy as np


MIN_RAID_USERS = 400
MIN_VIEWERS_DESTINATION = 200


def get_raids():
    raids = []

    # get the filenames of events
    filenames = [x for x in os.listdir("downloaded_events") if "template" not in x]

    for f in filenames:
        with open("downloaded_events/" + f, "r") as file:
            for line in file:
                if "\traid\t" in line:
                    # print(line, f)
                    # get the channel name
                    raided_channel_name = f.split(".")[0].strip()
                    # get the raid datetime
                    raid_datetime = line.split("\t")[0].strip()
                    # get the raid viewers
                    raid_viewers = line.split("\t")[3].strip()

                    # add the raid to the dictionary
                    if int(raid_viewers) > MIN_RAID_USERS:
                        raids.append({"raid_datetime": raid_datetime, "raided_channel": raided_channel_name, "raid_viewers": raid_viewers})

    return raids


def get_viewers_after_raids(raids):
    viewers_after_raids = []
    # viewers_after_raid = [
    #   {"channel": channel1, "datetime": 24-01-01_00-00-00, "raid_viewers": 1000, "after_raid_viewers_count": [200, 1200, 1150, 900, ...]}, 
    #   {"channel": channel2, "datetime": 24-01-15_21-30-29, "raid_viewers": 1257, "after_raid_viewers_count": [500, 1487, 1123, 951, ...]},
    #   ...
    # ]

    streams_info = [x for x in os.listdir("streams_info") if "template" not in x]
    streams_info.sort()

    bar = progressbar.ProgressBar(maxval=len(raids), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, raid in enumerate(raids):
        bar.update(i+1)

        # from streams info take the numbers of viewers before and after the raid
        raided_channel = raid["raided_channel"]
        raid_datetime = raid["raid_datetime"]
        raid_viewers = int(raid["raid_viewers"])

        # get a sub list of streams info with only the files 5 minutes before the raid and 60 minutes after the raid
        streams_info_sublist = []
        r_datetime = datetime.strptime(raid_datetime, "%y-%m-%d_%H-%M-%S")
        for s in streams_info:
            s_datetime = datetime.strptime(s.split(".")[0].strip("streams_info"), "%Y-%m-%d_%H-%M-%S")
            if r_datetime - timedelta(minutes=2) <= s_datetime <= r_datetime + timedelta(minutes=60):
                streams_info_sublist.append(s)

            if s_datetime > r_datetime + timedelta(minutes=60):
                break

        streams_info_sublist.sort()

        viewers_count_list = []
        for s in streams_info_sublist:
            with open("streams_info/" + s, "r") as file:
                for line in file:
                    if raided_channel in line:
                        viewers_count_list.append(int(line.split("\t")[2].strip()))

        # find the time when the raid happened
        raid_found = False
        try:
            for i in range(10):
                if viewers_count_list[i+1] - viewers_count_list[i] > 0.5 * raid_viewers:
                    raid_found = True
                    viewers_count_list = viewers_count_list[i:]
                    break
        except:
            raid_found = False
            

        # check that the destination channel has at least MIN_VIEWERS_DESTINATION viewers
        if raid_found and viewers_count_list[0] > MIN_VIEWERS_DESTINATION:
            viewers_after_raids.append({"channel": raided_channel, "datetime": raid_datetime, "raid_viewers": raid_viewers, "after_raid_viewers_count": viewers_count_list})

    bar.finish()

    return viewers_after_raids


def normalize_viewers_count(viewers_after_raids):
    for raid in viewers_after_raids:
        old_viewers_count_list = raid["after_raid_viewers_count"]

        # normalize the viewers count
        new_viewers_count_list = []
        for i in range(len(old_viewers_count_list)):
            if i == 0:
                new_viewers_count_list.append(100)
            else:
                new_viewers_count_list.append(((old_viewers_count_list[i] - old_viewers_count_list[0]) / raid["raid_viewers"])*100)

        raid["after_raid_viewers_count"] = new_viewers_count_list

    return viewers_after_raids


def get_mean_viewers_after_raids(viewers_after_raids):
    mean_viewers_after_raid = [0] * 60
    counters = [0] * 60

    for i in range(60):
        for raid in viewers_after_raids:
            try:
                mean_viewers_after_raid[i] += raid["after_raid_viewers_count"][i]
                counters[i] += 1
            except:
                pass

    for i in range(60):
        try:
            mean_viewers_after_raid[i] = round(mean_viewers_after_raid[i] / counters[i], 2)
        except:
            pass

    return mean_viewers_after_raid


def draw_graph(mean_viewers_after_raid):

    x = np.arange(60)
    y = mean_viewers_after_raid

    plt.plot(x, y)

    ax = plt.gca()
    ax.set_xlim([0, 54])
    ax.set_ylim([0, 100])

    plt.xlabel('Time after the raid (minutes)')
    plt.ylabel('viewers arrived from raid')

    plt.savefig("analysis_results/mean_viewers_after_raid.png")


def main():
    viewers_after_raids = []

    raids = get_raids()

    print(f"> Found {len(raids)} raids")

    viewers_after_raids = get_viewers_after_raids(raids)
    viewers_after_raids = normalize_viewers_count(viewers_after_raids)

    mean_viewers_after_raid = get_mean_viewers_after_raids(viewers_after_raids)

    # save the data in a csv file
    with open("analysis_results/post_raid_viewers_flow.csv", "w") as file:
        file.write("time\tmean_viewers\n")
        for i, v in enumerate(mean_viewers_after_raid):
            file.write(f"{i}\t{v}\n")

    draw_graph(mean_viewers_after_raid)


if __name__ == '__main__':
    main()
