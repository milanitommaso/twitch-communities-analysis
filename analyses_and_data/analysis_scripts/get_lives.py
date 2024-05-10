import os
from datetime import datetime
import progressbar

INIT_KEEP_CHANNEL_COUNT = 2

def parse_timestamp(timestamp_str):
    return datetime.strptime(timestamp_str, "streams_info%Y-%m-%d_%H-%M-%S.txt")

def process_files(input_directory, output_file):
    files = [f for f in sorted(os.listdir(input_directory)) if not f.startswith('.') and 'template' not in f.lower() and f.endswith('.txt')]
    files = files[::5]  # take only 1 file every 5 files (1 file every 5 minutes)

    current_lives = {}

    bar = progressbar.ProgressBar(maxval=len(files), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    with open(output_file, 'w') as output:
        for i, file_name in enumerate(files):
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
                            output.write(f'{channel}\t{timestamp_start}\t{timestamp_end}\n')
                        channels_to_delete.append(channel)

            for channel in channels_to_delete:
                del current_lives[channel]

            bar.update(i+1)

        bar.finish()


if __name__ == '__main__':
    input_directory = 'streams_info'
    output_file = 'lives.txt'
    process_files(input_directory, output_file)
