from imhotep.tools import Tool
from collections import defaultdict
import re
import os


class Flake8Linter(Tool):
    regex = re.compile(r'(?P<filename>.*):(?P<line_num>\d+):\d+: (?P<message>.*)')
    def invoke(self, dirname, filenames=set(), **kwargs):
        retval = defaultdict(lambda: defaultdict(list))

        # If filenames is set then make sure we only execute flake8
        # for directories containing these filenames.  We chose not to
        # directly execute flake for these filenames because doing
        # would cause flake8 to disrespect 'excludes' config
        # directive.
        if filenames:
            dirnames = []
            cmd = 'flake8 '
            for filename in filenames:
                if filename.endswith('.py'):
                    filedirname = os.path.dirname(os.path.join(dirname, filename))
                    dirnames.append(filedirname)

            # Make sure that we don't have both foo/bar and foo/ in
            # our list, or errors foo/bar/tza.py will appear twice.
            cleaned_dirnames = []
            for dire in sorted(dirnames, key=lambda x: len(x)):
                for cleaned_dirname in cleaned_dirnames:
                    if dire.startswith(cleaned_dirname):
                        break
                else:
                    cleaned_dirnames.append(dire)

            cmd = 'flake8 %s' % ' '.join(cleaned_dirnames)
            
        else:
            cmd = 'flake8 %s' % dirname

        output = self.executor(cmd)
        for line in output.split('\n'):
            match = self.regex.search(line)
            if match is not None:
                filename = match.group('filename')[len(dirname)+1:]
                retval[filename][match.group('line_num')].append(match.group('message'))
        return retval
