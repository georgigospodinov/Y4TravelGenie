import copy
import random
import sys

if "." not in sys.path:
    sys.path.insert(0, ".")

import part1.network as net
import part1.datasets as ds

clf: net.MLPClassifier = net.load_backup()
questions: list = []
# List of lists
answers: list = [[]]
attempted_guesses = set([])
SUCCESSFUL_GUESS, UNSUCCESSFUL_GUESS, IMPOSSIBLE_TO_GUESS = 0, 1, -1


def get_questions_file():
    return ds.get_data_folder() + "questions.txt"


def load_questions():
    file = open(get_questions_file())
    for line in file:
        questions.append(line.strip())
    file.close()


def add_alternatives(first: bool, target_list: list = None):
    a, b = (1, 0) if first else (0, 1)
    alternative: list = []
    if target_list is None:
        target_list = answers
    for ans in target_list:
        alt: list = ans.copy()
        alt.append(b)
        alternative.append(alt)
        ans.append(a)

    for alt in alternative:
        target_list.append(alt)


def try_parse_response(response: str):
    response = response.strip().lower()
    if response == "yes" or response == "yep":
        for ans in answers:
            ans.append(1)
    elif response == "no" or response == "nope":
        for ans in answers:
            ans.append(0)
    elif response == "probably not" or response == "maybe not":
        add_alternatives(False)
    elif response == "probably" or response == "maybe":
        add_alternatives(True)
    elif response == "idk" or response == "dk":
        add_alternatives(True)
    elif response == "i don't know" or response == "don't know":
        add_alternatives(True)
    elif response == "i dont know" or response == "dont know":
        add_alternatives(True)
    else:
        return False
    return True


def parse_response(question: str):
    print(question)
    res: str = sys.stdin.readline()
    while not try_parse_response(res):
        print("Failed to parse response \"{0}\"".format(res.strip()))
        res = sys.stdin.readline()


def determine_destination(answer_lists: list):
    possible: list = net.predict(clf, answer_lists)
    occurrences: dict = {}
    # Count occurrences.
    for dst in possible:
        if dst in attempted_guesses:
            continue
        c = occurrences.get(dst) if dst in occurrences.keys() else 0
        occurrences[dst] = c + 1
    if "debug" in sys.argv:
        print("occurrences =", occurrences)
    # Nothing was counted, fail now
    if len(occurrences) == 0:
        return IMPOSSIBLE_TO_GUESS, ""
    # Determine best guess based on highest occurrence.
    best_guess, high_count = "", 0
    first_index_of_best = 0
    for dst, count in occurrences.items():
        if count > high_count:
            best_guess, high_count = dst, count
            first_index_of_best = possible.index(best_guess)
        elif count == high_count:
            first_index_of_dst = possible.index(dst)
            # Have we found something closer to the first element?
            if first_index_of_dst < first_index_of_best:
                best_guess, high_count = dst, count
                first_index_of_best = first_index_of_dst

    print("Is your dream destination", best_guess + "?")
    attempted_guesses.add(best_guess)
    response = sys.stdin.readline().strip().lower()
    success = SUCCESSFUL_GUESS if response == "yes" or response == "yep" else UNSUCCESSFUL_GUESS
    return success, best_guess


def custom_sort(potentials: list):
    """
    Sorts the given list based on distance from the first element.
    Each element must be a list of integers. Distance between two such lists 'a' and 'b' is calculated as
    the sum of differences abs(a[i] - b[i]) for i between 0 and the length of the lists.
    All lists must be of the same length.

    :param potentials: the list to sort
    """
    constant = potentials[0]

    # The evaluation function that calculates the distance between the current and the first list
    def evaluate(p):
        d: int = 0
        for i, v in enumerate(p):
            d += abs(v - constant[i])
        return d

    potentials.sort(key=evaluate)


def guess():
    potentials: list = copy.deepcopy(answers)
    for i in range(len(answers[0]), len(questions)):
        b = bool(random.getrandbits(1))
        add_alternatives(b, potentials)
    custom_sort(potentials)
    if "debug" in sys.argv:
        print("potentials =", potentials)
    return determine_destination(potentials)


def ask_questions():
    part: int = 2
    # Double // divides and rounds down. Negate, divide and round down, then negate to obtain division with rounding up
    size = len(questions)
    threshold = -(-size // part + 1)
    for i, q in enumerate(questions):
        parse_response(q)
        # Do not do anything else if the threshold has not been reached.
        if i < threshold:
            continue
        # The threshold has been reached, set new one and make early guess
        part *= 2
        next_part = size // part
        if next_part == 1:
            threshold = size - 1
        else:
            threshold += next_part
        success, g = guess()
        if success == SUCCESSFUL_GUESS:
            return True, g
        # Do not surrender early if running in 'user' mode. Need answers from user.
        elif not ds.user and success == IMPOSSIBLE_TO_GUESS:
            break
    return False, ""


def main():
    load_questions()
    success, g = ask_questions()
    if success:
        print("Guessed successfully!")
    else:
        print("Can not guess!")


if __name__ == '__main__':
    main()
