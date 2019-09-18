import os
import sys

# Ignore deprecation warning produced by scikit-learn.
prev_err = sys.stderr
sys.stderr = None
from sklearn.externals import joblib
from sklearn.metrics import mean_squared_error
from sklearn.neural_network import MLPClassifier

sys.stderr = prev_err

if "." not in sys.path:
    sys.path.insert(0, ".")

import part1.datasets as ds

MAX_ERROR: float = 0.03
LEARNING_RATE: float = 0.1
MOMENTUM: float = 0.4
MAX_ITERATIONS: int = 100000


def get_network_filename():
    if ds.user:
        return "assets/neuralnets/user.net"
    elif ds.extra:
        return "assets/neuralnets/extra.net"
    else:
        return "assets/neuralnets/basic.net"


def as_ml_data(ml_set: dict):
    inputs: list = []
    output: list = []
    for ins, out in ml_set.items():
        inputs.append(list(ins))
        output.append(out)
    return inputs, output


def create_classifier(hidden_neurons: int, logging=False):
    return MLPClassifier(solver="sgd", activation="logistic", learning_rate_init=LEARNING_RATE, momentum=MOMENTUM,
                         hidden_layer_sizes=(hidden_neurons,), tol=1e-8, max_iter=MAX_ITERATIONS, n_iter_no_change=500,
                         verbose=logging)


def write_first_column(source_filename: str, chart_filename: str, hidden_neurons: int):
    chart_file = open(chart_filename, "w")
    chart_file.write(str(hidden_neurons) + "\n")
    src = open(source_filename)
    for line in src:
        parts: list = line.split(", loss = ")
        if len(parts) != 2:
            break
        chart_file.write(parts[1])
    src.close()
    chart_file.close()


def write_next_column(source_filename: str, chart_filename: str, hidden_neurons: int):
    chart_file = open(chart_filename)
    my_temp_filename = "my_temp.csv"
    temp = open(my_temp_filename, "w")
    chart_line = chart_file.readline().strip()
    temp.write(chart_line + "," + str(hidden_neurons) + "\n")
    last_chart_line = chart_line
    src = open(source_filename)
    last_source_line: str
    for line in src:
        parts: list = line.split(", loss = ")
        if len(parts) != 2:
            break
        chart_line = chart_file.readline().strip() + ","
        if chart_line == ",":
            chart_line = last_chart_line
        last_source_line = parts[1]
        temp.write(chart_line + last_source_line)
        last_chart_line = chart_line
    last_chart_line = chart_file.readline().strip() + ","
    while last_chart_line != ",":
        temp.write(last_chart_line + last_source_line)
        last_chart_line = chart_file.readline().strip() + ","
    src.close()
    temp.close()
    chart_file.close()
    os.remove(chart_filename)
    os.rename(my_temp_filename, chart_filename)


def store_training_data(source_filename: str, hidden_neurons: int):
    chart_prefix = "extra" if ds.extra else "basic"
    chart_prefix = "user" if ds.user else chart_prefix
    chart_name = chart_prefix + "_" + str(LEARNING_RATE) + "_" + str(MOMENTUM) + "_" + str(MAX_ITERATIONS)
    chart_filename = "assets/charts/" + chart_name + ".csv"
    try:
        write_next_column(source_filename, chart_filename, hidden_neurons)
    except FileNotFoundError:
        write_first_column(source_filename, chart_filename, hidden_neurons)


def train_with(hidden_neurons: int, train_x: list, train_y: list, test_x: list, test_y: list):
    logging: bool = "chart" in sys.argv
    clf = create_classifier(hidden_neurons, logging)
    if not logging:
        sys.stderr = None
        clf.fit(train_x, train_y)
        sys.stderr = prev_err
        return clf, mean_squared_error(test_y, clf.predict(test_x))

    old_stdout, temp_filename = sys.stdout, "temp.csv"
    sys.stdout = open(temp_filename, "w")
    old_stderr, sys.stderr = sys.stderr, None
    clf.fit(train_x, train_y)
    sys.stderr = old_stderr
    sys.stdout.close()
    sys.stdout = old_stdout
    y_predicted = clf.predict(test_x)
    error = mean_squared_error(test_y, y_predicted)
    store_training_data(temp_filename, hidden_neurons)
    os.remove(temp_filename)
    return clf, error


def train_new():
    filename: str = get_network_filename()
    train_x, train_y = as_ml_data(ds.training)
    test_x, test_y = as_ml_data(ds.testing)
    init_hidden: int = 2 * (len(train_x[0]) + len(train_y[0])) // 3
    init_hidden += init_hidden // 4
    least_error, best_hidden_count = 1.0, -1
    best_network: MLPClassifier
    error: float
    for hidden_neurons in range(init_hidden, 0, -1):
        clf, error = train_with(hidden_neurons, train_x, train_y, test_x, test_y)
        # Keep track of best result.
        if error < least_error:
            least_error = error
            best_hidden_count = hidden_neurons
            best_network = clf
        if error < MAX_ERROR:
            msg = "{0} hidden neurons produced an error of {1:0.2f} which is sufficiently good."
            print(msg.format(best_hidden_count, least_error))
            break
    if error >= MAX_ERROR:
        msg = "Failed to converge with error of {0:0.2f} or lower. Using {1} hidden neurons for error of {2:0.2f}."
        print(msg.format(MAX_ERROR, best_hidden_count, least_error))
    joblib.dump(best_network, filename)
    return best_network


def load_old():
    return joblib.load(get_network_filename())


def load_backup():
    filename: str = ds.get_data_folder() + "network.net"
    return joblib.load(filename)


def get_prediction(clf: MLPClassifier, pattern: list):
    try:
        prediction = tuple(clf.predict([pattern])[0])
        return ds.code_destinations[prediction]
    except KeyError:
        prob = clf.predict_proba([pattern])[0]
        index, value = -1, 0.0
        for i, p in enumerate(prob):
            if p >= value:
                index, value = i, p
        result: list = []
        for i, _ in enumerate(prob):
            result.append(int(i == index))
        return ds.code_destinations[tuple(result)]


def check_performance(clf: MLPClassifier):
    test_x, test_y = as_ml_data(ds.testing)
    test_prediction: list = clf.predict(test_x)
    score = mean_squared_error(test_y, test_prediction)
    print("test error {0:0.2f}".format(score))
    print("actual   predicted")
    for i, predicted in enumerate(test_prediction):
        pattern = test_x[i]
        actual = ds.code_destinations[tuple(ds.testing[tuple(pattern)])]
        try:
            res = ds.code_destinations[tuple(predicted)]  # Only re-calculate prediction for invalid keys
        except KeyError:
            res = get_prediction(clf, pattern)
        print(actual, res)


def predict(clf: MLPClassifier, input_patterns: list):
    destinations: list = []
    for pattern in input_patterns:
        dst = get_prediction(clf, pattern)
        destinations.append(dst)
    return destinations


def main():
    clf = train_new() if "train" in sys.argv else load_old()
    check_performance(clf)


if __name__ == '__main__':
    main()
