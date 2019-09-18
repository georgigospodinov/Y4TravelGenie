import os
import sys

if "." not in sys.path:
    sys.path.insert(0, ".")

import part1.datasets as ds

most_dreamed_destinations: dict = {}


def log_learning(destination: str, feature: str = "", answer: str = ""):
    """
    Write in the report file that a new location has been learned.
    Also calls count_dream to count off the destination.

    :param destination: the new destination that has been learned
    :param feature: the distinguishing feature for that destination
    :param answer: the answer to the question about this feature for this destination
    """
    learnings = open(ds.get_data_folder() + "learnings.txt", "a")
    learnings.write(destination + " " + feature + " " + answer + "\n")
    learnings.close()
    count_dream(destination)


def count_dream(destination: str):
    counts_fn = ds.get_data_folder() + "dream_counts.txt"
    counts = open(counts_fn)
    temp_fn = "assets/data/temp.txt"
    temp = open(temp_fn, "x")
    new_entry = True
    for line in counts:
        parts: list = line.strip().split(" ")
        if parts[0] == destination:
            line = destination + " " + str(int(parts[1]) + 1) + "\n"
            new_entry = False
        temp.write(line)
    if new_entry:
        temp.write(destination + " 1\n")
    counts.close()
    temp.close()
    os.remove(counts_fn)
    os.rename(temp_fn, counts_fn)


def count_answers(answers: list):
    counts_fn = ds.get_data_folder() + "answer_counts.txt"
    counts = open(counts_fn)
    temp_fn = "assets/data/temp.txt"
    temp = open(temp_fn, "x")
    for i, line in enumerate(counts):
        true_false_counts: list = line.strip().split(" ")
        true_count = int(true_false_counts[0])
        false_count = int(true_false_counts[1])

        # Catch the case when an early guess has been made and not all questions have been asked.
        if i < len(answers[0]):
            # Take the answer to the i-th question.
            a = answers[0][i]
            # Check if it's the same in all sequences (i.e. it is 'yes' or 'no', and it is not 'probably').
            same_across_all_sequences: bool = True
            for ans in answers:
                if ans[i] != a:
                    same_across_all_sequences = False
                    break
            # Only count the answer if it has been 'yes' or 'no'.
            if same_across_all_sequences:
                if a == 1:
                    true_count += 1
                elif a == 0:
                    false_count += 1

        temp.write(str(true_count) + " " + str(false_count) + "\n")
    counts.close()
    temp.close()
    os.remove(counts_fn)
    os.rename(temp_fn, counts_fn)
