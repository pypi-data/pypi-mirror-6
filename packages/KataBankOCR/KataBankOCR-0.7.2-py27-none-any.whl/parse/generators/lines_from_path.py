import fileinput

def lines_from_path(path):
    "generator that yields Lines either from Path or from StdIn"
    for line in fileinput.input(path):
        yield str(line).rstrip('\n')
