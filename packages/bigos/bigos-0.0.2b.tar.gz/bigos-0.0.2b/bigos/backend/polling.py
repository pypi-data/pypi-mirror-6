import os
import stat
import itertools
from time import sleep

class Event:
    def __init__(self, path, type_, stat_):
        self.path = path
        self.type = type_
        self.stat = stat_

    @property
    def is_dir(self):
        return bool(stat.S_ISDIR(self.stat.st_mode))

def scan_files(dir_path, d):
    previous_fs = list(d.keys())
    events = []

    for root, dirs, files in os.walk(dir_path):
        for f in itertools.chain(files, dirs):
            path = os.path.join(root, f)
            stat_ = os.stat(path)
            try:
                old_stat = d[path]
                if old_stat[stat.ST_MTIME] != stat_[stat.ST_MTIME]:
                    events.append(Event(path, 'modified', stat_))
                if old_stat[stat.ST_ATIME] != stat_[stat.ST_ATIME]:
                    events.append(Event(path, 'read', stat_))
            except KeyError:
                events.append(Event(path, 'created', stat_))
            d[path] = stat_

    for path in previous_fs:
        if path not in d:
            events.append(Event(path, 'removed', None))

    return events

def generate_events(dir_path):
    fs_dict = {}
    scan_files(dir_path, fs_dict)
    while True:
        sleep(5)
        evs = scan_files(dir_path, fs_dict)
        if evs:
            yield evs
