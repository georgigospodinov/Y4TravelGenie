import os
import random
import shutil
import sys

if "." not in sys.path:
    sys.path.insert(0, ".")

import part1.datasets as ds
import part1.network as net
import part2.genie as genie
import part3.reporting as reporting


def get_binary_input(can_quit: bool):
    failed_input_message = "Please enter \"yes\" or \"no\"."
    if can_quit:
        failed_input_message += " Alternatively you can \"quit\"."
    while True:
        response = sys.stdin.readline().strip().lower()
        if response == "yes" or response == "yep" or response == "sure":
            return True
        if response == "no" or response == "nope" or response == "no way":
            return False
        if (response == "idk" or response == "quit") and can_quit:
            return None
        print(failed_input_message)


def user_will_not_teach():
    print("You have defeated me. Congratulations!")
    # No learning unless running in user mode.
    if not ds.user:
        return True

    print("Would you tell me your destination? [yes/no]")
    return not get_binary_input(False)


def obtain_question():
    print("What is the name of your destination?")
    destination: str = sys.stdin.readline().strip()
    if destination in ds.destinations:
        print("Oh! I know about this location! I will learn from your answers!")
        return destination, "", ""
    print("What is its distinguishing feature?")
    feature: str = sys.stdin.readline().strip()
    if feature in ds.features:
        print("Oh! I know this feature! I will learn from your answers!")
        return destination, feature, ""
    print("What question should I ask about it?")

    while True:
        question: str = sys.stdin.readline().strip()
        if not question.endswith("?"):
            question += "?"
        if question not in genie.questions:
            break
        print("Sorry, I am already asking this question for another feature. Please, enter a new questions.")
    return destination, feature, question


def ask_for(meta_question: str, dst: str):
    print(meta_question.format(dst))
    b = get_binary_input(True)
    if b is None:
        return lambda: random.getrandbits(1)
    elif b:
        return lambda: 1
    else:
        return lambda: 0


def ask_for_all_known_destinations(question: str, new_destination: str):
    meta_question: str = "What is the answer to \"" + question + "\" if your dream location was {0}?"
    answers: dict = {}
    for dst in ds.destinations:
        answers[dst] = ask_for(meta_question, dst)
    answers[new_destination] = ask_for(meta_question, new_destination)
    return answers


def save_question(question: str):
    file = open(genie.get_questions_file(), "a")
    file.write("\n" + question)
    file.close()


def get_destination_from(line: str):
    destination: str = ""
    for c in line:
        try:
            int(c)
        except ValueError:
            destination += c
    return destination


def append_answers(answers: dict, target_fn: str):
    target_file = open(target_fn)
    temp_fn = "assets/data/temp.txt"
    temp_file = open(temp_fn, "x")
    for i, line in enumerate(target_file):
        line = line.strip()
        destination = get_destination_from(line)
        # Start with a new line character if this is not the first line.
        line = ("\n" if i > 0 else "") + line[:-len(destination)] + str(answers[destination]()) + destination
        temp_file.write(line)
    temp_file.close()
    target_file.close()
    os.remove(target_fn)
    os.rename(temp_fn, target_fn)


def append_new_destination(guessing_answers: list, destination: str, answer_function=lambda: ""):
    train_fn, _ = ds.get_data_sets_file_names()
    train_file = open(train_fn, "a")
    for ans in guessing_answers:
        line: str = ""
        for i in ans:
            line += str(i)
        line += str(answer_function())
        line += destination
        train_file.write("\n" + line)
    train_file.close()


def update_data(question: str, answers: dict):
    save_question(question)
    train_fn, test_fn = ds.get_data_sets_file_names()
    append_answers(answers, train_fn)
    append_answers(answers, test_fn)


def append_feature(feature: str):
    feature_file = open(ds.get_data_folder() + "features.txt", "a")
    feature_file.write("\n" + feature)
    feature_file.close()


def learn():
    destination, feature, question = obtain_question()
    if question == "":
        append_new_destination(genie.answers, destination)
        reporting.log_learning(destination, feature)
        return

    answers = ask_for_all_known_destinations(question, destination)
    update_data(question, answers)
    append_new_destination(genie.answers, destination, answers[destination])
    append_feature(feature)
    ans = "Yes" if answers[destination]() == 1 else "No"
    reporting.log_learning(destination, feature, ans)


def retrain():
    ds.clear()
    ds.load()
    net.train_new()
    net_name = ds.get_data_folder() + "network.net"
    os.remove(net_name)
    shutil.copy(net.get_network_filename(), net_name)


def main():
    genie.load_questions()
    success, guess = genie.ask_questions()
    if success:
        print("Guessed successfully!")
        if ds.user:
            reporting.count_dream(guess)
        return

    if user_will_not_teach():
        return

    reporting.count_answers(genie.answers)
    learn()
    retrain()


if __name__ == '__main__':
    main()
