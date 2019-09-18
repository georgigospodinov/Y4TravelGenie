import sys

features: set = set([])
destinations: list = []
destination_codes: dict = {}
code_destinations: dict = {}
# map input tuples to code
training: dict = {}
testing: dict = {}
USER: str = "user"
EXTRA: str = "extra"
extra: bool = EXTRA in sys.argv
user: bool = USER in sys.argv


def get_data_folder():
    if user:
        return "assets/data/user/"
    elif extra:
        return "assets/data/extra/"
    else:
        return "assets/data/basic/"


def parse_line(line: str, destination_inputs: dict):
    line = line.strip()
    in_pattern: list = []
    dst: str = ""
    for c in line:
        try:
            in_pattern.append(int(c))
        except ValueError:
            dst = dst + c
    if dst not in destinations:
        destinations.append(dst)
    if dst not in destination_inputs:
        destination_inputs[dst] = []
    destination_inputs.get(dst).append(in_pattern)


def load_set(filename: str, target_dict: dict):
    file = open(filename)
    # Maps destinations to an array to input patterns.
    destination_inputs: dict = {}
    for line in file:
        parse_line(line, destination_inputs)
    file.close()
    encode_destinations()
    for dst, in_patterns in destination_inputs.items():
        for pattern in in_patterns:
            target_dict[tuple(pattern)] = destination_codes[dst]


def encode_destinations():
    count: int = len(destinations)
    for i, dst in enumerate(destinations):
        code: list = []
        for j in range(i):
            code.append(0)
        code.append(1)
        for j in range(i + 1, count):
            code.append(0)
        destination_codes[dst] = code
        code_destinations[tuple(code)] = dst


def clear():
    training.clear()
    testing.clear()
    code_destinations.clear()
    destination_codes.clear()
    destinations.clear()


def get_data_sets_file_names():
    folder = get_data_folder()
    return folder + "training.set", folder + "testing.set"


def load():
    training_filename, testing_filename = get_data_sets_file_names()
    load_set(training_filename, training)
    load_set(testing_filename, testing)


def get_features_filename():
    return get_data_folder() + "features.txt"


def load_features():
    features_file = open(get_features_filename())
    for line in features_file:
        features.add(line.strip())
    features_file.close()


load()
load_features()
if __name__ == '__main__':
    for p, dst_code in training.items():
        print(p, dst_code)
    for p, dst_code in testing.items():
        print(p, dst_code)
