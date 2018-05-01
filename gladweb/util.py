import os
from datetime import datetime
from time import time as timestamp

import shutil


def convert_if_timestamp(time):
    if isinstance(time, int) or isinstance(time, float):
        return datetime.fromtimestamp(time)


# https://github.com/notifico/notifico/blob/master/notifico/util/pretty.py
def pretty_date(time, now=None):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """

    if now is None:
        now = timestamp()

    now = convert_if_timestamp(now)
    time = convert_if_timestamp(time)

    diff = now - time
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(second_diff / 60) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(second_diff / 3600) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff / 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff / 30) + " months ago"
    return str(day_diff / 365) + " years ago"


def write_dir_to_zipfile(path, zipf, exclude=None):
    if exclude is None:
        exclude = []

    for root, dirs, files in os.walk(path):
        for file_ in files:
            if file_ in exclude:
                continue

            zipf.write(
                os.path.join(root, file_),
                os.path.relpath(os.path.join(root, file_), path)
            )


def remove_file_or_dir(path):
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)
    else:
        shutil.rmtree(path)
