import fileinput
import logging
import os

log = logging.getLogger('common')


def dinput(prompt, default):
    """
    Works like input method but with the ability to specify default message
    """
    return input("{} (default: {}):".format(prompt, default)) or default


def replace_line(file_name, origin, replacement, log):
    replaced = False
    for line in fileinput.input(file_name, inplace=1):
        if origin in line and not replaced:
            print(replacement)
            log.info('Line "%s" has been replaced by "%s" in %s', origin, replacement, file_name)
            replaced = True
        else:
            print(line, end="")


def insert_lines(file_name, lines, condition):
    matched, inserted = matching_function(condition), False
    for i, line in enumerate(fileinput.input(file_name, inplace=1)):
        if matched(i, line) and not inserted:
            for s in lines:
                print(s, end='\n')
                log.info('Line "%s" has been inserted into %s', s, file_name)
            inserted = True
        print(line, end="")


def matching_function(condition):
    if condition.isdigit():
        return lambda index, line: int(condition) - 1 == index
    else:
        return lambda index, line: condition in line


class Config(object):
    DEFAULT_RCFILE_NAME = '~/.fitbitrc'

    def __init__(self, default_dir):
        filename = os.path.expanduser(self.DEFAULT_RCFILE_NAME)
        if not os.path.exists(filename):
            rep_location = input('Fitbit conf file does not exist. Please, specify your weightsite repository location:')
            file = open(filename, 'w+')
            file.write('weightsite=' + rep_location)
            file.flush()
        with open(filename, 'rt') as f:
            self.config = dict(line.strip().split('=') for line in f)
        self.default_dir = self.config['weightsite'] + default_dir

    def dir(self):
        return self.default_dir