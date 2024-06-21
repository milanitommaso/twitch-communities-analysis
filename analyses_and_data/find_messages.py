import os
import progressbar


def get_chat_files():
    chat_files = []

    dirs = os.listdir("analyses_and_data/downloaded_chats")
    dirs = [dir for dir in dirs if "template" not in dir]

    for dir in dirs:
        files = os.listdir("analyses_and_data/downloaded_chats/" + dir)
        for file in files:
            chat_files.append("analyses_and_data/downloaded_chats/" + dir + "/" + file)

    return chat_files


def find_messages(chat_files, word):
    messages = []

    bar = progressbar.ProgressBar(maxval=len(chat_files), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, chat_file in enumerate(chat_files):
        bar.update(i)
        with open(chat_file) as f:
            for line in f:
                if word in line:
                    messages.append((line.strip(), chat_file))
                    print(line + "\n" + chat_file + "\n\n")

    bar.finish()

    return messages


def main():
    chat_files = get_chat_files()

    messages = find_messages(chat_files, word="word_to_find")

    # save the messages in a txt file
    with open("messages.txt", "w") as f:
        for message in messages:
            f.write(message[0] + "  -_-_-_-_-_-_-_-_-  " + message[1] + "\n")




if __name__ == "__main__":
    main()
