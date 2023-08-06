
import os
import re


# file reading utility function
def fread(filename, split=False, keepnl=False):
    """
    may raise IOError exceptions from file operations
    """
    result = ""
    if split:
        result = []
    with open(filename) as f:
        for line in f:
            if line == '\n':
                continue
            if split:
                result.append(line.replace('\n', ''))
            else:
                result += line
    return result


# Natural Sort lists
"""
http://stackoverflow.com/questions/5254021/python-human-sort-of-numbers-with-alpha-numeric-but-in-pyqt-and-a-lt-oper/5254534#5254534
http://stackoverflow.com/questions/5295087/how-to-sort-alphanumeric-list-of-django-model-objects
"""


def natural_key(value):
    """
    Creates a human appropriate key from value

    Logically, humans see 10 as coming after 2, where normal
    computer ordering leaves you with ['1', '10', '2'] in many
    cases, so this creates a better key for ordering things the
    way we think about things

    Example:
        packages = list(AvatarItemPackage.get_user_packages(request.user))
        packages.sort(key=lambda x: natural_key(x.name))
    """
    # regex looking for integers or floats
    tokens = re.split('(\d*\.\d+|\d+)', value)
    # swapcase makes uppercase get sorted after lowercase
    return tuple((e.swapcase() if i % 2 == 0 else float(e)) for i, e in enumerate(tokens))


def natural_sort(iterable, key):
    # determine which type it is

    # perform the sorting
    # still needs error checking for getattr
    return iterable.sort(key=lambda x: natural_key(getattr(x, key)))


class alist(list):
    def natsort(self, key):
        # still needs error checking for getattr
        self.sort(key=lambda x: natural_key(getattr(x, key)))

