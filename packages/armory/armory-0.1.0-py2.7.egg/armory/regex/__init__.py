
import os
import re

'''
implement xml schema matching and dictionary collect
'''


class ReMatch(object):
    SHIFT_CHARACTERS = r'!@#\$%\^&\(\)_\-\+='
    source = None
    pattern = None

    def __init__(self, source, pattern):
        self.source = source
        self.pattern = pattern
        self.regex = re.compile(self.pattern)

    def collect(self):
        pass


class FileReMatch(ReMatch):

    def collect(self):
        # need to verify self.source is valid directory
        self.source = self.source if self.source else os.getcwd()
        self.matched = self._match_files(self.source, self.regex)

    def _match_files(self, path, pattern, fullpath=False):
        return [os.path.join(path, f) if fullpath else f for f in os.listdir(path) if pattern.match(f)]

    def _fn(self, filename, index=None):
        info = self.regex.match(filename).groupdict()
        return '%s_%s-%s%s' % (info['count'], info['event'], info['picture'], info['extension'])

    def rename_files(self):
        conversions = {f: self._fn(f, i) for i, f in enumerate(self.matched)}
        for oldname, newname in conversions.iteritems():
            os.rename(oldname, newname)
            print '%55s  ===>  %s' % (oldname, newname)



