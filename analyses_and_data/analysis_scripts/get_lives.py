import os
from datetime import datetime
import progressbar

EVERY_X_MINUTES = 5
INIT_KEEP_CHANNEL_COUNT = 4 # keep the channel for 4 files (4*EVERY_X_MINUTES minutes)


def parse_timestamp(timestamp_str):
    return datetime.strptime(timestamp_str, "streams_info%Y-%m-%d_%H-%M-%S.txt")


def get_year_month_from_streams_info_filename(filename):
    dt =  datetime.strptime(filename, "streams_info%Y-%m-%d_%H-%M-%S.txt")
    return dt.strftime("%Y%m")


def process_files(input_directory, years_months):
    files = [f for f in sorted(os.listdir(input_directory)) if not f.startswith('.') and 'template' not in f.lower() and f.endswith('.txt')]
    files = files[::EVERY_X_MINUTES]  # take only 1 file every X files (1 file every X minutes)

    current_lives = {}

    bar = progressbar.ProgressBar(maxval=len(files), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    res_str = ""

    for i, file_name in enumerate(files):
        # if the file is not in the months we want to process, skip it
        if get_year_month_from_streams_info_filename(file_name) not in years_months:
            bar.update(i+1)
            continue

        channels_to_delete = []
        file_path = os.path.join(input_directory, file_name)

        with open(file_path, 'r') as file:
            # print(f'> Processing {file_name}')
            current_file_channels = []

            for line in file:
                channel, category, viewer_count = line.strip().split('\t')
                timestamp_start = parse_timestamp(file_name)

                current_file_channels.append(channel)

                if channel not in current_lives:
                    current_lives[channel] = [channel, timestamp_start, None, INIT_KEEP_CHANNEL_COUNT]    # (channel, timestamp_start, timestamp_end, keep_channel_count)
                else:
                    current_lives[channel][3] = INIT_KEEP_CHANNEL_COUNT
                    current_lives[channel][2] = None
                
        for channel, [channel, timestamp_start, timestamp_end, keep_channel_count] in current_lives.items():
            if channel not in current_file_channels:
                current_lives[channel][3] -= 1

                if current_lives[channel][3] == 1:
                    current_lives[channel][2] = parse_timestamp(file_name)

                elif current_lives[channel][3] == 0:
                    total_time = (current_lives[channel][2] - current_lives[channel][1]).total_seconds()
                    if total_time > 1800:   # if live for less than 30 minutes, don't count it
                        res_str += f'{channel}\t{timestamp_start}\t{timestamp_end}\n'
                    channels_to_delete.append(channel)

        for channel in channels_to_delete:
            del current_lives[channel]

        bar.update(i+1)

    bar.finish()

    return res_str


def for_handler(years_months, version):
    input_directory = 'analyses_and_data/streams_info'
    return process_files(input_directory, years_months)


def main():
    years_months = ["202407"]

    input_directory = 'analyses_and_data/streams_info'
    res_str = process_files(input_directory, years_months)

    with open(f"analyses_and_data/analysis_results/lives202408.txt", "w") as file:
        file.write(res_str)


if __name__ == '__main__':
    main()
