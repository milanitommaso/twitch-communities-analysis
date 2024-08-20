import json
import glob


def get_version(months):
    if len(months) == 1:
        return months[0]
    else:
        return f"{months[0]}-{months[-1]}"


# CACHING HANDLER
def handle_lives(months):
    print("Running lives analysis")
    from analyses_and_data.analysis_scripts.get_lives import for_handler as lives_for_handler

    version = get_version(months)

    lives = lives_for_handler(months, version)

    with open(f"analyses_and_data/cached_data/lives{version}.txt", "w") as file:
        file.write(lives)

    print("Lives analysis completed")


def handle_lives_count(months):
    print("Running lives count analysis")
    from analyses_and_data.analysis_scripts.lives_count import for_handler as lives_count_for_handler 
    from analyses_and_data.analysis_scripts.lives_count import ANALYSES_REQUIRED as lives_count_analyses_required

    version = get_version(months)

    for analysis in lives_count_analyses_required:
        # check if the required analysis is in chached analyses folder
        if glob.glob(f"analyses_and_data/cached_data/{analysis}{version}.*"):
            continue

        if analysis not in analysis_handlers_bindings:
            raise Exception(f"Analysis {analysis} is required for lives_count analysis but no handler was found")

        # run the required analysis
        print(f"Running required analysis {analysis}")
        analysis_handlers_bindings[analysis]()

    lives_count = lives_count_for_handler(months, version)

    with open(f"analyses_and_data/cached_data/lives_count{version}.json", "w") as file:
        json.dump(lives_count, file, indent=4)

    print("Lives count analysis completed")


def handle_top_streamers_by_viewers(months):
    from analyses_and_data.analysis_scripts.top_streamers_by_viewers import for_handler as top_streamers_by_viewers_for_handler
    from analyses_and_data.analysis_scripts.top_streamers_by_viewers import ANALYSES_REQUIRED as top_streamers_by_viewers_analyses_required

    version = get_version(months)

    for analysis in top_streamers_by_viewers_analyses_required:
        # check if the required analysis is in chached analyses folder
        if glob.glob(f"analyses_and_data/cached_data/{analysis}{version}.*"):
            continue

        if analysis not in analysis_handlers_bindings:
            raise Exception(f"Analysis {analysis} is required for lives_count analysis but no handler was found")

        # run the required analysis
        print(f"Running required analysis {analysis}")
        analysis_handlers_bindings[analysis](months)

    top_streamers = top_streamers_by_viewers_for_handler(months, version)

    # save the top streamers to a json file
    with open(f"analyses_and_data/cached_data/top_streamers{version}.json", "w") as file:
        json.dump(top_streamers, file, indent=4)

    # save the top streamers to a txt file
    with open(f"analyses_and_data/cached_data/top_streamers{version}.txt", "w") as file:
        for streamer in top_streamers.keys():
            file.write(f"{streamer}\n")


# ANALYSES HANDLER

def handle_community_loyalty(months):
    from analyses_and_data.analysis_scripts.community_loyalty import for_handler as community_loyalty_for_handler
    from analyses_and_data.analysis_scripts.community_loyalty import ANALYSES_REQUIRED as community_loyalty_analyses_required

    version = get_version(months)

    for analysis in community_loyalty_analyses_required:
        # check if the required analysis is in chached analyses folder
        if glob.glob(f"analyses_and_data/cached_data/{analysis}{version}.*"):
            continue

        if analysis not in analysis_handlers_bindings:
            raise Exception(f"Analysis {analysis} is required for community_loyalty analysis but no handler was found")

        # run the required analysis
        print(f"Running required analysis {analysis}")
        analysis_handlers_bindings[analysis](months)

    community_loyalty = community_loyalty_for_handler(months, version)

    with open(f"website/static/analyses_results/community-loyalty/{version}.csv", "w") as file:
        file.write(community_loyalty)


def handle_emote_ratio(months):
    from analyses_and_data.analysis_scripts.emote_ratio import for_handler as emote_ratio_for_handler
    from analyses_and_data.analysis_scripts.emote_ratio import ANALYSES_REQUIRED as emote_ratio_analyses_required

    version = get_version(months)

    for analysis in emote_ratio_analyses_required:
        # check if the required analysis is in chached analyses folder
        if glob.glob(f"analyses_and_data/cached_data/{analysis}{version}.*"):
            continue

        if analysis not in analysis_handlers_bindings:
            raise Exception(f"Analysis {analysis} is required for emote_ratio analysis but no handler was found")

        # run the required analysis
        print(f"Running required analysis {analysis}")
        analysis_handlers_bindings[analysis](months)

    emote_ratio = emote_ratio_for_handler(months, version)

    with open(f"website/static/analyses_results/emotes-ratio/{version}.csv", "w") as file:
        file.write(emote_ratio)


def handle_messages_per_user(months):
    from analyses_and_data.analysis_scripts.messages_per_user import for_handler as messages_per_user_for_handler

    version = get_version(months)

    # take the data not from cached data but from the static folder in website
    if not glob.glob(f"website/static/analyses_results/turnout/{version}.csv"):
        print("Running required analysis turnout")
        handle_turnout(months)

    if not glob.glob(f"website/static/analyses_results/turnout-by-messages/{version}.csv"):
        print("Running required analysis turnout_by_messages")
        handle_turnout_by_messages(months)

    messages_per_user = messages_per_user_for_handler(version)

    with open(f"website/static/analyses_results/messages-per-user/{version}.csv", "w") as file:
        file.write(messages_per_user)


def handle_most_watched(months):
    from analyses_and_data.analysis_scripts.most_watched import for_handler as most_watched_for_handler
    from analyses_and_data.analysis_scripts.most_watched import ANALYSES_REQUIRED as most_watched_analyses_required

    version = get_version(months)

    for analysis in most_watched_analyses_required:
        # check if the required analysis is in chached analyses folder
        if glob.glob(f"analyses_and_data/cached_data/{analysis}{version}.*"):
            continue

        if analysis not in analysis_handlers_bindings:
            raise Exception(f"Analysis {analysis} is required for most_watched analysis but no handler was found")

        # run the required analysis
        print(f"Running required analysis {analysis}")
        analysis_handlers_bindings[analysis](months)

    most_watched = most_watched_for_handler(months, version)

    with open(f"website/static/analyses_results/most-watched/{version}.csv", "w") as file:
        file.write(most_watched)


def handle_post_raid_viewers(months):
    from analyses_and_data.analysis_scripts.post_raid_viewers_flow import for_handler as post_raid_viewers_for_handler
    from analyses_and_data.analysis_scripts.post_raid_viewers_flow import ANALYSES_REQUIRED as post_raid_viewers_analyses_required

    version = get_version(months)

    for analysis in post_raid_viewers_analyses_required:
        # check if the required analysis is in chached analyses folder
        if glob.glob(f"analyses_and_data/cached_data/{analysis}{version}.*"):
            continue

        if analysis not in analysis_handlers_bindings:
            raise Exception(f"Analysis {analysis} is required for post_raid_viewers analysis but no handler was found")

        # run the required analysis
        print(f"Running required analysis {analysis}")
        analysis_handlers_bindings[analysis](months)

    post_raid_viewers = post_raid_viewers_for_handler(months, version)

    with open(f"website/static/analyses_results/post-raid-viewers/{version}.csv", "w") as file:
        file.write(post_raid_viewers)


def handle_streamer_reach(months):
    from analyses_and_data.analysis_scripts.streamer_reach import for_handler as streamer_reach_for_handler
    from analyses_and_data.analysis_scripts.streamer_reach import ANALYSES_REQUIRED as streamer_reach_analyses_required

    version = get_version(months)

    for analysis in streamer_reach_analyses_required:
        # check if the required analysis is in chached analyses folder
        if glob.glob(f"analyses_and_data/cached_data/{analysis}{version}.*"):
            continue

        if analysis not in analysis_handlers_bindings:
            raise Exception(f"Analysis {analysis} is required for streamer_reach analysis but no handler was found")

        # run the required analysis
        print(f"Running required analysis {analysis}")
        analysis_handlers_bindings[analysis](months)

    streamer_reach = streamer_reach_for_handler(months, version)

    with open(f"website/static/analyses_results/streamer-reach/{version}.csv", "w") as file:
        file.write(streamer_reach)


def handle_streams_start(months):
    from analyses_and_data.analysis_scripts.streams_start import for_handler as streams_start_for_handler
    from analyses_and_data.analysis_scripts.streams_start import ANALYSES_REQUIRED as streams_start_analyses_required

    version = get_version(months)

    for analysis in streams_start_analyses_required:
        # check if the required analysis is in chached analyses folder
        if glob.glob(f"analyses_and_data/cached_data/{analysis}{version}.*"):
            continue

        if analysis not in analysis_handlers_bindings:
            raise Exception(f"Analysis {analysis} is required for streams_start analysis but no handler was found")

        # run the required analysis
        print(f"Running required analysis {analysis}")
        analysis_handlers_bindings[analysis](months)

    streams_start = streams_start_for_handler(months, version)

    with open(f"website/static/analyses_results/streams-start/{version}.csv", "w") as file:
        file.write(streams_start)


def handle_subs_impact(months):
    from analyses_and_data.analysis_scripts.subs_impact import for_handler as subs_impact_for_handler
    from analyses_and_data.analysis_scripts.subs_impact import ANALYSES_REQUIRED as subs_impact_analyses_required

    version = get_version(months)

    for analysis in subs_impact_analyses_required:
        # check if the required analysis is in chached analyses folder
        if glob.glob(f"analyses_and_data/cached_data/{analysis}{version}.*"):
            continue

        if analysis not in analysis_handlers_bindings:
            raise Exception(f"Analysis {analysis} is required for subs_impact analysis but no handler was found")

        # run the required analysis
        print(f"Running required analysis {analysis}")
        analysis_handlers_bindings[analysis](months)

    subs_impact = subs_impact_for_handler(months, version)

    with open(f"website/static/analyses_results/subscribers-impact/{version}.csv", "w") as file:
        file.write(subs_impact)


def handle_top_contributors_impact(months):
    from analyses_and_data.analysis_scripts.top_contributors_impact import for_handler as top_contributors_impact_for_handler
    from analyses_and_data.analysis_scripts.top_contributors_impact import ANALYSES_REQUIRED as top_contributors_impact_analyses_required

    version = get_version(months)

    for analysis in top_contributors_impact_analyses_required:
        # check if the required analysis is in chached analyses folder
        if glob.glob(f"analyses_and_data/cached_data/{analysis}{version}.*"):
            continue

        if analysis not in analysis_handlers_bindings:
            raise Exception(f"Analysis {analysis} is required for top_contributors_impact analysis but no handler was found")

        # run the required analysis
        print(f"Running required analysis {analysis}")
        analysis_handlers_bindings[analysis](months)

    top_contributors_impact = top_contributors_impact_for_handler(months, version)

    with open(f"website/static/analyses_results/top-contributors-impact/{version}.csv", "w") as file:
        file.write(top_contributors_impact)


def handle_turnout(months):
    from analyses_and_data.analysis_scripts.turnout import for_handler as turnout_for_handler
    from analyses_and_data.analysis_scripts.turnout import ANALYSES_REQUIRED as turnout_analyses_required

    version = get_version(months)

    for analysis in turnout_analyses_required:
        # check if the required analysis is in chached analyses folder
        if glob.glob(f"analyses_and_data/cached_data/{analysis}{version}.*"):
            continue

        if analysis not in analysis_handlers_bindings:
            raise Exception(f"Analysis {analysis} is required for turnout analysis but no handler was found")

        # run the required analysis
        print(f"Running required analysis {analysis}")
        analysis_handlers_bindings[analysis](months)

    turnout = turnout_for_handler(months)

    with open(f"website/static/analyses_results/turnout/{version}.csv", "w") as file:
        file.write(turnout)


def handle_turnout_by_messages(months):
    from analyses_and_data.analysis_scripts.turnout_messages import for_handler as turnout_messages_for_handler
    from analyses_and_data.analysis_scripts.turnout_messages import ANALYSES_REQUIRED as turnout_messages_analyses_required

    version = get_version(months)

    for analysis in turnout_messages_analyses_required:
        # check if the required analysis is in chached analyses folder
        if glob.glob(f"analyses_and_data/cached_data/{analysis}{version}.*"):
            continue

        if analysis not in analysis_handlers_bindings:
            raise Exception(f"Analysis {analysis} is required for turnout_by_messages analysis but no handler was found")

        # run the required analysis
        print(f"Running required analysis {analysis}")
        analysis_handlers_bindings[analysis](months)

    turnout = turnout_messages_for_handler(months)

    with open(f"website/static/analyses_results/turnout-by-messages/{version}.csv", "w") as file:
        file.write(turnout)


def handle_watched_channels(months):
    from analyses_and_data.analysis_scripts.watched_channels import for_handler as watched_channels_for_handler
    from analyses_and_data.analysis_scripts.watched_channels import ANALYSES_REQUIRED as watched_channels_analyses_required

    version = get_version(months)

    for analysis in watched_channels_analyses_required:
        # check if the required analysis is in chached analyses folder
        if glob.glob(f"analyses_and_data/cached_data/{analysis}{version}.*"):
            continue

        if analysis not in analysis_handlers_bindings:
            raise Exception(f"Analysis {analysis} is required for watched_channels analysis but no handler was found")

        # run the required analysis
        print(f"Running required analysis {analysis}")
        analysis_handlers_bindings[analysis](months)

    watched_channels = watched_channels_for_handler(months, version)

    with open(f"website/static/analyses_results/watched-channels/{version}.csv", "w") as file:
        file.write(watched_channels)


def handle_graph(months):
    from analyses_and_data.analysis_scripts.graph import for_handler as graph_for_handler
    from analyses_and_data.analysis_scripts.graph import ANALYSES_REQUIRED as graph_analyses_required

    version = get_version(months)

    for analysis in graph_analyses_required:
        # check if the required analysis is in chached analyses folder
        if glob.glob(f"analyses_and_data/cached_data/{analysis}{version}.*"):
            continue

        if analysis not in analysis_handlers_bindings:
            raise Exception(f"Analysis {analysis} is required for graph analysis but no handler was found")

        # run the required analysis
        print(f"Running required analysis {analysis}")
        analysis_handlers_bindings[analysis](months)

    edges = graph_for_handler(months, version)
    with open(f"analyses_and_data/analysis_results/edges{version}.csv", "w") as file:
        file.write(edges)


def live_stats():
    from analyses_and_data.analysis_scripts.live_stats import for_handler as live_stats_for_handler

    live_stats = live_stats_for_handler()

    with open("website/static/analyses_results/live_stats.json", "w") as file:
        json.dump(live_stats, file, indent=4)


def main():
    handle_community_loyalty(["202407"])


if __name__ == "__main__":
    analysis_handlers_bindings = {
        "lives": handle_lives,
        "lives_count": handle_lives_count,
        "top_streamers": handle_top_streamers_by_viewers,
        "turnout": handle_turnout,
        "turnout_by_messages": handle_turnout_by_messages
    }
    
    main()
