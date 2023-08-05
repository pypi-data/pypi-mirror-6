#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test suite for pyformat."""

from __future__ import unicode_literals

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest

import pyformat


ROOT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))


if (
    'PYFORMAT_COVERAGE' in os.environ and
    int(os.environ['PYFORMAT_COVERAGE'])
):
    PYFORMAT_COMMAND = ['coverage', 'run', '--branch', '--parallel',
                        '--omit=*/distutils/*,*/site-packages/*',
                        os.path.join(ROOT_DIRECTORY, 'pyformat.py')]
else:
    # We need to specify the executable to make sure the correct Python
    # interpreter gets used.
    PYFORMAT_COMMAND = [sys.executable,
                        os.path.join(
                            ROOT_DIRECTORY,
                            'pyformat.py')]  # pragma: no cover


class TestUnits(unittest.TestCase):

    def test_format_code(self):
        self.assertEqual("x = 'abc' \\\n    'next'\n",
                         pyformat.format_code(
                             'x = "abc" \\\n"next"\n'))

    def test_format_code_with_aggressive(self):
        self.assertEqual('True\n',
                         pyformat.format_code(
                             'import os\nTrue\n',
                             aggressive=True))

    def test_format_code_without_aggressive(self):
        self.assertEqual('import os\nTrue\n',
                         pyformat.format_code(
                             'import os\nTrue\n',
                             aggressive=False))

    def test_format_code_with_unicode(self):
        self.assertEqual("x = 'abc' \\\n    'ö'\n",
                         pyformat.format_code(
                             'x = "abc" \\\n"ö"\n'))


class TestSystem(unittest.TestCase):

    def test_diff(self):
        with temporary_file('''\
import os
x = "abc"
''') as filename:
            output_file = io.StringIO()
            pyformat._main(argv=['my_fake_program', filename],
                           standard_out=output_file,
                           standard_error=None)
            self.assertEqual('''\
@@ -1,2 +1,2 @@
 import os
-x = "abc"
+x = 'abc'
''', '\n'.join(output_file.getvalue().split('\n')[2:]))

    def test_diff_with_aggressive(self):
        with temporary_file('''\
import os
x = "abc"
''') as filename:
            output_file = io.StringIO()
            pyformat._main(argv=['my_fake_program', '--aggressive', filename],
                           standard_out=output_file,
                           standard_error=None)
            self.assertEqual('''\
@@ -1,2 +1 @@
-import os
-x = "abc"
+x = 'abc'
''', '\n'.join(output_file.getvalue().split('\n')[2:]))

    def test_diff_with_empty_file(self):
        with temporary_file('') as filename:
            output_file = io.StringIO()
            pyformat._main(argv=['my_fake_program', filename],
                           standard_out=output_file,
                           standard_error=None)
            self.assertEqual('', output_file.getvalue())

    def test_diff_with_encoding_declaration(self):
        with temporary_file("""\
# coding: utf-8
import re
import os
import my_own_module
x = 1
""") as filename:
            output_file = io.StringIO()
            pyformat._main(argv=['my_fake_program', '--aggressive', filename],
                           standard_out=output_file,
                           standard_error=None)
            self.assertEqual("""\
 # coding: utf-8
-import re
-import os
 import my_own_module
 x = 1
""", '\n'.join(output_file.getvalue().split('\n')[3:]))

    def test_diff_with_nonexistent_file(self):
        output_file = io.StringIO()
        pyformat._main(argv=['my_fake_program', 'nonexistent_file'],
                       standard_out=output_file,
                       standard_error=output_file)
        self.assertIn('no such file', output_file.getvalue().lower())

    def test_verbose(self):
        output_file = io.StringIO()
        pyformat._main(argv=['my_fake_program', '--verbose', __file__],
                       standard_out=output_file,
                       standard_error=output_file)
        self.assertIn('.py', output_file.getvalue())

    def test_in_place(self):
        with temporary_file('''\
if True:
    x = "abc"
''') as filename:
            output_file = io.StringIO()
            pyformat._main(argv=['my_fake_program', '--in-place', filename],
                           standard_out=output_file,
                           standard_error=None)
            with open(filename) as f:
                self.assertEqual('''\
if True:
    x = 'abc'
''', f.read())

    def test_multiple_jobs(self):
        with temporary_file('''\
if True:
    x = "abc"
''') as filename:
            output_file = io.StringIO()
            pyformat._main(argv=['my_fake_program', '--in-place',
                                 '--jobs=2', filename],
                           standard_out=output_file,
                           standard_error=None)
            with open(filename) as f:
                self.assertEqual('''\
if True:
    x = 'abc'
''', f.read())

    def test_multiple_jobs_should_require_in_place(self):
        output_file = io.StringIO()
        pyformat._main(argv=['my_fake_program',
                             '--jobs=2', __file__],
                       standard_out=output_file,
                       standard_error=output_file)

        self.assertIn('requires --in-place', output_file.getvalue())

    def test_jobs_less_than_one_should_default_to_cpu_count(self):
        args = pyformat.parse_args(['my_fake_program',
                                    '--jobs=0', __file__])

        self.assertGreater(args.jobs, 0)

    def test_ignore_hidden_directories(self):
        with temporary_directory() as directory:
            with temporary_directory(prefix='.',
                                     directory=directory) as inner_directory:

                with temporary_file("""\
if True:
    x = "abc"
""", directory=inner_directory):

                    output_file = io.StringIO()
                    pyformat._main(argv=['my_fake_program',
                                         '--recursive',
                                         directory],
                                   standard_out=output_file,
                                   standard_error=None)
                    self.assertEqual(
                        '',
                        output_file.getvalue().strip())

    def test_recursive(self):
        with temporary_directory() as directory:
            with temporary_file("""\
if True:
    x = "abc"
""", prefix='food', directory=directory):

                output_file = io.StringIO()
                pyformat._main(argv=['my_fake_program',
                                     '--recursive',
                                     '--exclude=zap',
                                     '--exclude=x*oo*',
                                     directory],
                               standard_out=output_file,
                               standard_error=None)
                self.assertEqual("""\
@@ -1,2 +1,2 @@
 if True:
-    x = "abc"
+    x = 'abc'
""", '\n'.join(output_file.getvalue().split('\n')[2:]))

    def test_exclude(self):
        with temporary_directory() as directory:
            with temporary_file("""\
if True:
    x = "abc"
""", prefix='food', directory=directory):

                output_file = io.StringIO()
                pyformat._main(argv=['my_fake_program',
                                     '--recursive',
                                     '--exclude=zap',
                                     '--exclude=*oo*',
                                     directory],
                               standard_out=output_file,
                               standard_error=None)
                self.assertEqual(
                    '',
                    output_file.getvalue().strip())

    def test_end_to_end(self):
        with temporary_file("""\
import os
x = "abc"
""") as filename:
            process = subprocess.Popen(PYFORMAT_COMMAND + [filename],
                                       stdout=subprocess.PIPE)
            self.assertEqual("""\
 import os
-x = "abc"
+x = 'abc'
""", '\n'.join(process.communicate()[0].decode('utf-8').split('\n')[3:]))


@contextlib.contextmanager
def temporary_file(contents, directory='.', prefix=''):
    """Write contents to temporary file and yield it."""
    f = tempfile.NamedTemporaryFile(suffix='.py', prefix=prefix,
                                    delete=False, dir=directory)
    try:
        f.write(contents.encode('utf8'))
        f.close()
        yield f.name
    finally:
        import os
        os.remove(f.name)


@contextlib.contextmanager
def temporary_directory(directory='.', prefix=''):
    """Create temporary directory and yield its path."""
    temp_directory = tempfile.mkdtemp(prefix=prefix, dir=directory)
    try:
        yield temp_directory
    finally:
        import shutil
        shutil.rmtree(temp_directory)


if __name__ == '__main__':
    unittest.main()
