import os

def write_first_column(source_filename: str, chart_filename: str, hidden_neurons: int):
    print("first column")
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
    print("next column")
    my_temp_filename = "my_temp.csv"
    temp = open(my_temp_filename, "w")
    chart_line = chart_file.readline().strip()
    temp.write(chart_line + "," + str(hidden_neurons) + "\n")
    last_chart_line = chart_line
    src = open(source_filename)
    last_source_line: str
    print("adding new lines")
    for line in src:
        parts: list = line.split(", loss = ")
        if len(parts) != 2:
            break
        chart_line = chart_file.readline().strip() + ","
        if chart_line == ",":
            chart_line = last_chart_line
        last_source_line = parts[1]
        print(chart_line + last_source_line)
        temp.write(chart_line + last_source_line)
        last_chart_line = chart_line
    print("copyig old lines")
    last_chart_line = chart_file.readline().strip() + ","
    while last_chart_line != ",":
        print(last_chart_line + last_source_line)
        temp.write(last_chart_line + last_source_line)
        last_chart_line = chart_file.readline().strip() + ","
    print("done")
    src.close()
    temp.close()
    chart_file.close()
    os.remove(chart_filename)
    os.rename(my_temp_filename, chart_filename)


def create_chart(source_filename: str, hidden_neurons: int):
    chart_filename = "my_chart.csv"
    try:
        write_next_column(source_filename, chart_filename, hidden_neurons)
    except FileNotFoundError:
        write_first_column(source_filename, chart_filename, hidden_neurons)


create_chart("my_src.csv", 5)
