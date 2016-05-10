__author__ = '@dominofire'

def parse_stderr_file(fn):
    with open(fn, 'r') as fh:
        time_lines = fh.readlines()[-3:]
