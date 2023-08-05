from StringIO import StringIO
from unittest import TestCase

from verge import cli


class TestParseCLI(TestCase):
    def test_when_nothing_is_given_read_lines_from_stdin(self):
        stdin = StringIO("1\n2\n3\n")
        arguments = cli.parse(
            ["program", "arguments", "2", "program"],
            stdin=stdin,
        )
        arguments["arguments"] = list(arguments["arguments"])
        self.assertEqual(
            arguments, {
                "command": ["program", "arguments", "2", "program"],
                "arguments": ["1", "2", "3"],
            },
        )

    def test_command_line_arguments(self):
        arguments = cli.parse(["program", ":::", "1", "2", "3"])
        arguments["arguments"] = list(arguments["arguments"])
        self.assertEqual(
            arguments, {
                "command": ["program"],
                "arguments": ["1", "2", "3"],
            },
        )
