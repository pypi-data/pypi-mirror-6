import shutil
import tempfile
import unittest

import os.path as op

from macholib import mach_o

import machotools

from machotools.tests.common import DYLIB_DIRECTORY, FILES_TO_DEPENDENCY_NAMES
from machotools.tests.common import BaseMachOCommandTestCase

class TestDependencies(BaseMachOCommandTestCase):
    def test_simple_read(self):
        for f, dependencies in FILES_TO_DEPENDENCY_NAMES.iteritems():
            self.assertEqual(len(machotools.dependencies(f)), 1)
            self.assertEqual(machotools.dependencies(f)[0], dependencies)

    def test_simple_write(self):
        r_dependencies = ["bar.2.0.0.dylib", "/usr/lib/libSystem.B.dylib"]

        old_dependency = "bar.1.0.0.dylib"
        new_dependency = "bar.2.0.0.dylib"

        temp_fp = tempfile.NamedTemporaryFile()
        main = op.join(DYLIB_DIRECTORY, "main")
        with open(main, "rb") as fp:
            shutil.copyfileobj(fp, temp_fp)

        machotools.change_dependency(temp_fp.name, old_dependency, new_dependency)

        self.assertEqual(machotools.dependencies(temp_fp.name)[0], r_dependencies)
        filters = {mach_o.LC_LOAD_DYLIB: lambda x: (x[0], x[1])}
        self.assert_commands_equal(main, temp_fp.name, filters)
