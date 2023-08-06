import os
import tempfile


class TestModule(object):
    def __init__(self, testdir, interpreter, modules, test_case, keep_module=False):
        self.testdir = testdir
        self.interpreter = interpreter
        self.modules = modules
        self.test_case = test_case
        self.keep_module = keep_module

        self.passed = None
        self.stderr = None
        self.filepath = None

    def assemble(self):
        (fd, self.filepath) = tempfile.mkstemp(
            dir=self.testdir,
            prefix='%s_' % self.test_case,
            suffix='.js',
            text=True,
        )

        try:
            # concatenate modules
            for module in self.modules:
                with open(module, 'rt') as f:
                    content = f.read()

                content = '%s\n\n' % content
                content = content.encode('utf8')
                os.write(fd, content)

            # invoke the test case function
            content = '%s();\n' % self.test_case
            content = content.encode('utf8')
            os.write(fd, content)

        finally:
            os.close(fd)

    def run(self):
        self.assemble()

        try:
            passed, stderr = self.interpreter.run_module(self.filepath)
            if passed:
                self.passed = True

            else:
                self.passed = False
                self.stderr = stderr

        finally:
            if not self.keep_module:
                os.unlink(self.filepath)
