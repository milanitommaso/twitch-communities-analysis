

def handle_turnout():
    from analyses_and_data.analysis_scripts.turnout import for_handler as turnout_for_handler

    months = ["202401", "202402", "202403"]
    version = "202401-202403"

    turnout = turnout_for_handler(months)

    with open(f"website/static/analyses_results/turnout/{version}.csv", "w") as file:
        file.write(turnout)


def handle_turnout_by_messages():
    from analyses_and_data.analysis_scripts.turnout_messages import for_handler as turnout_messages_for_handler

    months = ["202401", "202402", "202403"]
    version = "202401-202403"

    turnout = turnout_messages_for_handler(months)

    with open(f"website/static/analyses_results/turnout-by-messages/{version}.csv", "w") as file:
        file.write(turnout)


def main():
    handle_turnout()
    handle_turnout_by_messages()
    





if __name__ == "__main__":
    main()
