import json
from datetime import datetime, timedelta
from pprint import pprint
from collections import Counter
import progressbar


START_DATETIME = datetime.strptime("2023-12-01 00:00:00", '%Y-%m-%d %H:%M:%S')
END_DATETIME = datetime.strptime("2024-03-31 23:59:59", '%Y-%m-%d %H:%M:%S')


def get_chatters(streamers_in):
    chatters = {}
    current_start_datetime = START_DATETIME

    print("> Getting chatters...")

    while END_DATETIME > current_start_datetime:
        # open chatters file
        filename = "chatters/" + current_start_datetime.strftime('%Y%m%d_%H%M') + '.json'
        with open(filename, "r") as f:
            c = json.load(f)

        for streamer in c:
            if streamer not in streamers_in:
                continue

            if streamer not in chatters:
                chatters[streamer] = c[streamer]
            else:
                chatters[streamer] += c[streamer]

        # increment the hour
        current_start_datetime += timedelta(hours=1)

    return chatters


def find_edges(chatters_in):
    print("> Finding edges...")
    edges = []

    bar = progressbar.ProgressBar(maxval=len(chatters_in), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, streamer1 in enumerate(chatters_in):

        for streamer2 in chatters_in:
            if streamer1 == streamer2:
                continue

            common_chatters = list((Counter(chatters_in[streamer1]) & Counter(chatters_in[streamer2])).elements())
            weight = len(common_chatters)

            if weight == 0:
                continue

            check = True
            for edge in edges:
                if (edge[0] == streamer1 and edge[1] == streamer2) or (edge[0] == streamer2 and edge[1] == streamer1):
                    check = False
                    break
            
            if check:
                edges.append([streamer1, streamer2, weight])

        bar.update(i)

    bar.finish()

    # take only edges with weight > 0
    edges = [edge for edge in edges if edge[2] > 0]

    # save edges to file
    with open("analysis_results/edges.csv", "w") as f:
        f.write("Source\tTarget\tWeight\n")
        for edge in edges:
            f.write(f"{edge[0]}\t{edge[1]}\t{edge[2]}\n")


def get_nodes(number_of_nodes):
    print("> Getting nodes...")
    nodes = []

    with open('top_streamers.txt', 'r') as f:
        lines = f.readlines()[0:number_of_nodes]
    for l in lines:
        nodes.append(l.strip())

    # in top_stremers.txt there are only the streamers with at least 10 lives

    # # save nodes to file
    # with open("nodes.csv", "w") as f:
    #     for node in nodes:
    #         f.write(f"{node}\n")

    return nodes


if __name__ == "__main__":
    nodes = get_nodes(number_of_nodes=400)

    chatters = get_chatters(nodes)

    find_edges(chatters)
