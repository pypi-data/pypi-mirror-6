#
#  Copyright (C) 2014 Dell, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import unittest
import sys
import tempfile
import shutil
import traceback
import json
from StringIO import StringIO

import mock

import blockade.cli


INT_ENV = "BLOCKADE_INTEGRATION_TESTS"
INT_SKIP = (not os.getenv(INT_ENV), "export %s=1 to run" % INT_ENV)


class FakeExit(BaseException):
    def __init__(self, rc):
        self.rc = rc


def example_config_path(filename):
    example_dir = os.path.join(os.path.dirname(__file__), "../..", "examples")
    example_dir = os.path.abspath(example_dir)
    if not os.path.exists(example_dir):
        raise Exception("example config directory not found: %s" % example_dir)

    config_path = os.path.join(example_dir, filename)
    if not os.path.exists(config_path):
        raise Exception("example config not found: %s" % config_path)
    return config_path


class IntegrationTests(unittest.TestCase):
    """Integration tests that run the full CLI args down.

    Tests that are Linux and Docker only should be decorated with:
        @unittest.skipIf(*INT_SKIP)

    They will only be run when BLOCKADE_INTEGRATION_TESTS=1 env is set.
    """

    sysexit_patch = None
    stderr_patch = None
    tempdir = None
    oldcwd = None

    def setUp(self):
        self.sysexit_patch = mock.patch("sys.exit")
        self.mock_sysexit = self.sysexit_patch.start()

        def exit(rc):
            raise FakeExit(rc)

        self.mock_sysexit.side_effect = exit

        self.tempdir = tempfile.mkdtemp()
        self.oldcwd = os.getcwd()
        os.chdir(self.tempdir)

    def tearDown(self):
        if self.sysexit_patch:
            self.sysexit_patch.stop()

        if self.oldcwd:
            os.chdir(self.oldcwd)
        if self.tempdir:
            try:
                shutil.rmtree(self.tempdir)
            except Exception:
                pass

    def call_blockade(self, *args):
        stdout = StringIO()
        stderr = StringIO()
        with mock.patch("blockade.cli.puts") as mock_puts:
            mock_puts.side_effect = stdout.write

            with mock.patch("blockade.cli.puts_err") as mock_puts_err:
                mock_puts_err.side_effect = stderr.write

                try:
                    blockade.cli.main(args)
                except FakeExit, e:
                    if e.rc != 0:
                        raise
                return (stdout.getvalue(), stderr.getvalue())

    def test_badargs(self):
        with mock.patch("sys.stderr"):
            with self.assertRaises(FakeExit) as cm:
                self.call_blockade("--notarealarg")

            self.assertEqual(cm.exception.rc, 2)

    @unittest.skipIf(*INT_SKIP)
    def test_containers(self):
        config_path = example_config_path("sleep/blockade.yaml")

        # TODO make this better. so far we just walk through all
        # the major operations, but don't really assert anything
        # other than exit code.
        try:
            self.call_blockade("-c", config_path, "up")

            self.call_blockade("-c", config_path, "status")
            stdout, _ = self.call_blockade("-c", config_path, "status",
                                           "--json")
            parsed = json.loads(stdout)
            self.assertEqual(len(parsed), 3)

            self.call_blockade("-c", config_path, "flaky", "c1")
            self.call_blockade("-c", config_path, "slow", "c2", "c3")
            self.call_blockade("-c", config_path, "fast", "c3")

            # make sure it is harmless for call fast when nothing is slow
            self.call_blockade("-c", config_path, "fast", "--all")

            with self.assertRaises(FakeExit):
                self.call_blockade("-c", config_path, "slow", "notarealnode")

            self.call_blockade("-c", config_path, "partition", "c1,c2", "c3")
            self.call_blockade("-c", config_path, "join")

            stdout, _ = self.call_blockade("-c", config_path, "logs", "c1")
            self.assertEquals("I am c1", stdout.strip())

        finally:
            try:
                self.call_blockade("-c", config_path, "destroy")
            except Exception:
                print "Failed to destroy Blockade!"
                traceback.print_exc(file=sys.stdout)
