import fnmatch
import logging
import os
import re
from .common import *


def print_files(conf_dir, message, files):
    print(message + '\n' + '\n'.join(file.replace(conf_dir, '') for file in files))


def filter_files(conf_dir, files):
    while True:
        regex = input('Enter regex to filter files (Use empty string for all files or to stop filtering):')
        if not regex:
            break
        files = [file for file in files if re.search(regex, file.replace(conf_dir, ''))]
        print_files(conf_dir, 'Filtered files', files)
    return files


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    log = logging.getLogger('ch')
    config = Config('/site/conf/webapp')
    conf_dir = dinput('Dir to search in', config.dir())
    file_name = dinput('Enter the name of the file you want to modify', 'environment.properties')
    files = []
    for root, dirnames, filenames in os.walk(conf_dir):
        for filename in fnmatch.filter(filenames, file_name):
            files.append(os.path.join(root, filename))
    print_files(conf_dir, 'Found files', files)
    files = filter_files(conf_dir, files)

    print_files(conf_dir, 'Final files', files)
    action = input(
        'What do you want to do? (use a for append, r for replace, i for insert):') #a - append, r - replace, i-insert
    if action == 'a':
        append_line = input('Enter the line you want to append:')
        if append_line:
            for file in files:
                with open(file, 'a') as f:
                    f.write('\n' + append_line)
                    log.info('Line %s has been appended to %s', append_line, f.name)
    elif action == 'r':
        origin, replacement = input('Enter the key to replace:'), input('Enter the replacement line:')
        for file in files:
            replace_line(file, origin, replacement, log)
    elif action == 'i':
        condition_str = input('Enter the line number or a string above which you want to insert:')
        lines = []
        while True:
            line = input('Enter the line to insert (click enter to finish):')
            if not line: break
            lines.append(line)
        for file in files:
            insert_lines(file, lines, condition_str)

