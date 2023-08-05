from __future__ import unicode_literals

import helper
import os
import subprocess
import sys
import tempfile
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO
from rock import cli, utils
from rock.exceptions import ConfigError
from rock.project import Project
from helper import Args


def config_file(name):
    with open(os.path.join(helper.CONFIG_PATH, name)) as f:
        return f.read().strip()


class CliTestCase(helper.unittest.TestCase):

    def setUp(self):
        helper.setenv()
        def execl(*args):
            self.args = args
        utils.os.execl = execl
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        self.stdout = sys.stdout = StringIO()
        self.stderr = sys.stderr = StringIO()

    def setTeardown(self):
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

    def test_project(self):
        self.assertTrue(isinstance(cli.project(Args()), Project))

    def test_config_json(self):
        import json
        cli.config(Args(), ['--format=json'])
        data1 = json.loads(self.stdout.getvalue().strip().replace(helper.ROOT_PATH, '<ROOT>'))
        data2 = json.loads(config_file('data.json'))
        self.assertEqual(data1, data2)

    def test_config_yaml(self):
        import yaml
        cli.config(Args(), ['--format=yaml'])
        data1 = yaml.safe_load(self.stdout.getvalue().strip().replace(helper.ROOT_PATH, '<ROOT>'))
        data2 = yaml.safe_load(config_file('data.json'))
        self.assertEqual(data1, data2)

    def test_env(self):
        cli.env(Args(), [])
        self.assertIn('export TEST_PATH="test_path"', self.stdout.getvalue())

    def test_runtime(self):
        cli.runtime(Args(), [])
        self.assertIn('test123', self.stdout.getvalue())

    def test_help(self):
        self.assertRaises(SystemExit, cli.main, ['--help'])
        self.assertEqual(self.stdout.getvalue(), cli.USAGE + '\n\n' + cli.HELP + '\n')

    def test_main_empty(self):
        stderr = sys.stderr
        argv = sys.argv
        try:
            sys.argv = []
            sys.stderr = StringIO()
            self.assertRaises(SystemExit, cli.main)
            self.assertIn('Usage: rock', sys.stderr.getvalue())
        finally:
            sys.argv = argv
            sys.stderr = stderr

    def test_main_valid(self):
        cli.main(argv=['--env', 'prod', 'runtime'])

    def test_main_invalid(self):
        stderr = sys.stderr
        try:
            sys.stderr = StringIO()
            self.assertRaises(SystemExit, cli.main, ['--path=%s/not-found' % helper.TESTS_PATH, 'run', 'ok'])
        finally:
            sys.stderr = stderr
