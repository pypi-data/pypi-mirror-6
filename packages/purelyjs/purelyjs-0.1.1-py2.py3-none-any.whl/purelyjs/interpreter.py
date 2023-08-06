import os
import tempfile

from .io import invoke


class Interpreter(object):
    # Assuming whatever is called "js" on the path is likely to work best
    known_engines = ['js', 'rhino']

    def __init__(self, exes=None):
        engines = exes if exes else self.known_engines
        self.exe = self.detect(engines)

        if not self.exe:
            raise RuntimeError("No js engine could be found, tried: %s"
                               % ', '.join(engines))

    def detect(self, engines):
        found = None

        for engine in engines:
            # NOTE: Very platform specific
            success, stdout, stderr = invoke(['which', engine])
            exe = stdout

            # command exists, try executing a module on it
            if success:
                if self.run_test_module(exe):
                    found = exe
                    break

        return found

    def run_test_module(self, exe):
        (fd, filepath) = tempfile.mkstemp()

        try:
            content = (
                'try {'
                '  print;'
                '} catch (e) {'
                '  if (e.name !== "ReferenceError") {'
                '    throw e;'
                '  }'
                '  print = console.log;'  # node.js
                '}'
                'print(1 + 3);')
            content = content.encode('utf8')
            os.write(fd, content)

            success, stdout, stderr = invoke([exe, filepath])
            content = stdout.decode('utf8')
            if success and '4' == content:
                return True

        finally:
            os.close(fd)
            os.unlink(filepath)

    def run_module(self, filepath):
        success, stdout, stderr = invoke([self.exe, filepath])
        return success, stderr
