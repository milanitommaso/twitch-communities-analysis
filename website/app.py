from flask import Flask, render_template, send_file, request
import os
import json
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config["DEBUG"] = True


def get_with_tousands_separators(number):
    return "{:,}".format(number)


def get_verions(stat):
    versions = {}

    # get the versions
    for file in sorted(os.listdir(f"static/analyses_results/{stat}"), reverse=True):
        if not file.endswith(".csv"):
            continue

        file = file.split(".")[0]

        if file == "last_30_days" or file == "last_7_days":
            name = file.replace("_", " ").title()
            versions[file] = name

        elif "-" in file:
            start_month = file.split("-")[0]
            end_month = file.split("-")[1]

            start_month = datetime.strptime(start_month, "%Y%m").strftime("%b %Y")
            end_month = datetime.strptime(end_month, "%Y%m").strftime("%b %Y")

            name = f"{start_month} - {end_month}"
            versions[file] = name
        else:
            month = datetime.strptime(file, "%Y%m").strftime("%b %Y")
            versions[file] = month

    return versions


@app.route('/')
def index():
    # get live stat
    with open("static/analyses_results/live_stats.json", "r") as f:
        live_stats = json.load(f)
    for k in live_stats:
        live_stats[k] = get_with_tousands_separators(live_stats[k])

    # most watched
    most_watched_by_timeslots = get_stat_data("most-watched", "last_7_days")

    if most_watched_by_timeslots == "not found":
        most_watched_by_timeslots = {"morning": {}, "afternoon": {}, "evening": {}, "night": {}}
    else:
        for t in most_watched_by_timeslots:
            most_watched_by_timeslots[t] = [f"{k} ({int(v)})" for k, v in most_watched_by_timeslots[t].items()]

    # get the version
    # get the previous month
    today = datetime.today()
    last_day_prev_month = today.replace(day=1) - timedelta(days=1)
    version = [last_day_prev_month.strftime("%Y%m"), last_day_prev_month.strftime("%B %Y")]

    return render_template("index.html", live_stats=live_stats, most_watched_by_timeslots=most_watched_by_timeslots, version=version)


@app.route('/graph/description')
def graph_description():

    # get graphs file from static/graphs folder
    graphs = {}
    for file in sorted(os.listdir("static/graphs")):
        if not file.endswith(".gexf"):
            continue

        file = file.split(".")[0]

        if "-" in file:
            start_month = file.split("-")[0]
            end_month = file.split("-")[1]

            start_month = datetime.strptime(start_month, "%Y%m").strftime("%b %Y")
            end_month = datetime.strptime(end_month, "%Y%m").strftime("%b %Y")

            name = f"{start_month} - {end_month}"
            id = file
            graphs[name] = id
        else:
            month = file
            month = datetime.strptime(month, "%Y%m").strftime("%b %Y")
            graphs[month] = file

    return render_template("graph_description.html" , graphs=graphs)


@app.route('/graph')
def graph():
    #get version from request
    version = request.args.get('v')

    if version is None:
        return "No version provided. Please provide a version."

    # get graphs file from static/graphs folder
    graphs = {}
    for file in sorted(os.listdir("static/graphs")):
        if not file.endswith(".gexf"):
            continue

        file = file.split(".")[0]

        if "-" in file:
            start_month = file.split("-")[0]
            end_month = file.split("-")[1]

            start_month = datetime.strptime(start_month, "%Y%m").strftime("%b %Y")
            end_month = datetime.strptime(end_month, "%Y%m").strftime("%b %Y")

            name = f"{start_month} - {end_month}"
            id = file
            graphs[name] = id
        else:
            month = file
            month = datetime.strptime(month, "%Y%m").strftime("%b %Y")
            graphs[month] = file
        
    if version not in graphs.values():
        return "Invalid version provided. Please provide a valid version."

    current_version = [version, list(graphs.keys())[list(graphs.values()).index(version)]]
    other_versions = {k: v for k, v in graphs.items() if v != version}

    return render_template(f"graph.html", current_version=current_version, other_versions=other_versions)


@app.route('/get_graph_file/<version>')
def get_graph_file(version):
    return send_file(f"static/graphs/{version}")


@app.route('/stats')
def stats():

    stats = {
    "most-watched":["Most Watched", "Discover the most watched channels across various timeslots: morning, afternoon, evening, and night."],
    "turnout":["Turnout", "Explore the viewership trends on Twitch at different times of the day and days of the week."],
    "turnout-by-messages":["Turnout by Messages", "Explore the volume of messages sent per minute on Twitch at different times of the day and days of the week."],
    "messages-per-user":["Messages Per User", "Explore the average number of messages sent per minute per user on Twitch at different times of the day and days of the week."],
    "top-contributors-impact":["Top Contributors Impact", "Analyze the influence of the top 10, 50, and 100 chatters on each channel."],
    "subscribers-impact":["Subscribers Impact", "Analyze the influence of subscribers on each channel."],
    "emotes-ratio":["Emotes Ratio", "Analyze the proportion of messages containing emotes sent on each channel."],
    "streams-start":["Streams Start", "Examine how viewer numbers fluctuate when a stream begins."],
    "post-raid-viewers":["Post-Raid Viewers", "Explore how viewer numbers change after a raid on the destination channel."],
    "watched-channels":["Watched Channels", "Examine how many users watch how many channels."],
    "streamer-reach":["Streamer Reach", "Explore the number of users who have sent at least one message in a channel."],
    "community-loyalty":["Community Loyalty", "Analyze how loyal a channel's community is by examining how many users watch other channels within that community."]
    }

    return render_template("stats.html", stats=stats)


@app.route('/stats/<stat>')
def stat(stat):
    all_versions = get_verions(stat)
    
    current_version = request.args.get('v')
    if current_version is None:
        current_version = list(all_versions.keys())[0]

    if current_version not in all_versions:
        return "Invalid version provided. Please provide a valid version."

    current_version = [current_version, all_versions[current_version]]

    # load analysis description
    with open("static/analysis_descriptions.json", "r") as f:
        analysis_description = json.load(f)[stat]

    return render_template(f"stats/{stat}.html", all_versions=all_versions, current_version=current_version, analysis_description=analysis_description, stat=stat)


@app.route('/get_stat_data/<stat>/<version>')
def get_stat_data(stat, version):
    data_ret = {}

    if stat == "most-watched":
        # open the data file

        try:
            with open(f"static/analyses_results/{stat}/{version}.csv", "r") as f:
                data = f.readlines()
        except:
            return "not found"

        timeslots = ["morning", "afternoon", "evening", "night"]
        for line in data:
            line = line.strip().split("\t")
            
            if len(line) == 1 and line[0] in timeslots:
                current_timeslot = line[0]
                data_ret[current_timeslot] = {}

            elif len(line) == 2:
                data_ret[current_timeslot][line[0]] = float(line[1])

            elif len(line) == 1 and line[0] not in timeslots:
                continue

        # take only the first 3 channels for each timeslot
        for timeslot in data_ret:
            data_ret[timeslot] = {k: data_ret[timeslot][k] for k in list(data_ret[timeslot].keys())[:5]}

        # order the channels by number of viewers
        for timeslot in data_ret:
            data_ret[timeslot] = {k: v for k, v in sorted(data_ret[timeslot].items(), key=lambda item: float(item[1]), reverse=True)}

    elif stat == "turnout" or stat == "turnout-by-messages" or stat == "messages-per-user":
        # open the data file
        try:
            with open(f"static/analyses_results/{stat}/{version}.csv", "r") as f:
                lines = f.readlines()
        except:
            return "not found"


        data_ret = {}
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for i in range(24):
            if i < 10:
                hour = f"0{i}"
            else:
                hour = f"{i}"

            for j in range(0, 59, 30):
                # get the time
                if j == 0:
                    minute = "00"
                else:
                    minute = str(j)
                
                time = f"{hour}:{minute}"

                data_ret[time] = {}
                for day in days:
                    data_ret[time][day] = 0

        for i, line in enumerate(lines):
            line = line.strip().split("\t")

            if i == 0:
                continue

            time = line[0]
            
            for j in range(7):
                data_ret[time][days[j]] = float(line[j+1])

    elif stat == "top-contributors-impact":
        # open the data file
        try:
            with open(f"static/analyses_results/{stat}/{version}.csv", "r") as f:
                lines = f.readlines()
        except:
            return "not found"

        data_ret = {}
        for i, line in enumerate(lines):
            line = line.strip().split("\t")

            if i == 0:
                continue

            if len(line) == 2:
                data_ret[line[0]] = float(line[1])

            elif len(line) == 3:
                data_ret[line[0]] = [float(line[1]), float(line[2])]

            elif len(line) == 4:
                data_ret[line[0]] = [float(line[1]), float(line[2]), float(line[3])]

    elif stat == "subscribers-impact" or stat == "emotes-ratio":
        # open the data file
        try:
            with open(f"static/analyses_results/{stat}/{version}.csv", "r") as f:
                lines = f.readlines()
        except:
            return "not found"

        data_ret = {}
        for i, line in enumerate(lines):
            line = line.strip().split("\t")

            if i == 0:
                continue

            if len(line) == 2:
                data_ret[line[0]] = float(line[1])

    elif stat == "streams-start" or stat == "post-raid-viewers":
        # open the data file
        try:
            with open(f"static/analyses_results/{stat}/{version}.csv", "r") as f:
                lines = f.readlines()
        except:
            return "not found"

        data_ret = {}
        for i, line in enumerate(lines):
            line = line.strip().split("\t")

            if i == 0:
                continue

            if len(line) == 2:
                data_ret[line[0]] = float(line[1].replace("%", ""))

    elif stat == "watched-channels" or stat == "streamer-reach":
        # open the data file
        try:
            with open(f"static/analyses_results/{stat}/{version}.csv", "r") as f:
                lines = f.readlines()
        except:
            return "not found"

        data_ret = {}
        for i, line in enumerate(lines):
            line = line.strip().split("\t")

            if i == 0:
                continue

            if len(line) == 2:
                data_ret[line[0]] = float(line[1].replace("%", ""))

    elif stat == "community-loyalty":
        # open the data file
        try:
            with open(f"static/analyses_results/{stat}/{version}.csv", "r") as f:
                lines = f.readlines()
        except:
            return "not found"

        data_ret = {}
        for i, line in enumerate(lines):
            line = line.strip().split("\t")
            if i == 0:
                continue

            slots = ["1", "2-3", "4-5", "6-10", "11-15", "16-20", "21+"]

            data_ret[line[0]] = {}
            for j in range(len(slots)):
                data_ret[line[0]][slots[j]] = float(line[j+1].replace("%", ""))

    else:
        pass

    return data_ret


@app.route('/special-analyses')
def special_analysis():
    return render_template("special_analyses.html")


@app.route('/about')
def about():
    return render_template("about.html")


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
