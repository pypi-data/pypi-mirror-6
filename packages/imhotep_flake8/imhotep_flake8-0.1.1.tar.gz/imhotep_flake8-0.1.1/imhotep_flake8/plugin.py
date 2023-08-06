from imhotep.tools import Tool
from collections import defaultdict
import re

class Flake8Linter(Tool):
    regex = re.compile(r'(?P<filename>.*):(?P<line_num>\d+):\d+: (?P<message>.*)')
    def invoke(self, dirname, filenames=set(), **kwargs):
        retval = defaultdict(lambda: defaultdict(list))

        cmd = 'flake8 %s' % dirname
        output = self.executor(cmd)
        for line in output.split('\n'):
            match = self.regex.search(line)
            if match is not None:
                filename = match.group('filename')[len(dirname)+1:]
                retval[filename][match.group('line_num')].append(match.group('message'))
        return retval
