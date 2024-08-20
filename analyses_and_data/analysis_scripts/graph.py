import json
from datetime import datetime, timedelta
import calendar
from pprint import pprint
from collections import Counter
import progressbar

ANALYSES_REQUIRED = ["top_streamers"]


def get_chatters(streamers_in, start_datetime, end_datetime):
    chatters = {}
    current_start_datetime = start_datetime

    print("> Getting chatters...")

    while end_datetime > current_start_datetime:
        # open chatters file
        filename = "analyses_and_data/chatters/" + current_start_datetime.strftime('%Y%m%d_%H%M') + '.json'
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

    return edges


def get_nodes(number_of_nodes, version):
    print("> Getting nodes...")
    nodes = []

    with open(f'analyses_and_data/cached_data/top_streamers{version}.txt', 'r') as f:
        lines = f.readlines()[0:number_of_nodes]
    for l in lines:
        nodes.append(l.strip())

    return nodes


def for_handler(years_months, version):
    ret_str = ""
    nodes = get_nodes(400, version)

    start_datetime = datetime.strptime(years_months[0], '%Y%m')

    end_datetime = datetime.strptime(years_months[-1], '%Y%m')
    last_day = calendar.monthrange(int(end_datetime.strftime('%Y')), int(end_datetime.strftime('%m')))[-1]
    end_datetime = end_datetime.replace(day = last_day, hour = 23, minute = 59)

    chatters = get_chatters(nodes, start_datetime, end_datetime)

    edges = find_edges(chatters)

    ret_str += "Source\tTarget\tWeight\n"
    for edge in edges:
        ret_str += f"{edge[0]}\t{edge[1]}\t{edge[2]}\n"

    return ret_str


def main():
    years_months = ["202401", "202402", "202403"]
    version = "202401-202403"

    nodes = get_nodes(400, version)

    start_datetime = datetime.strptime(years_months[0], '%Y%m')

    end_datetime = datetime.strptime(years_months[-1], '%Y%m')
    last_day = calendar.monthrange(int(end_datetime.strftime('%Y')), int(end_datetime.strftime('%m')))[-1]
    end_datetime = end_datetime.replace(day = last_day, hour = 23, minute = 59)

    chatters = get_chatters(nodes, start_datetime, end_datetime)

    edges = find_edges(chatters)

    # save edges to file
    with open("analyses_and_data/analysis_results/edges.csv", "w") as f:
        f.write("Source\tTarget\tWeight\n")
        for edge in edges:
            f.write(f"{edge[0]}\t{edge[1]}\t{edge[2]}\n")


if __name__ == "__main__":
    main()
