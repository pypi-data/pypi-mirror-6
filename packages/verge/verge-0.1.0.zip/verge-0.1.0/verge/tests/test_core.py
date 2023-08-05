from StringIO import StringIO
from unittest import TestCase

from twisted.internet.defer import inlineCallbacks
from twisted.trial.unittest import TestCase as TrialTestCase

from verge import core


class TestMain(TrialTestCase):
    @inlineCallbacks
    def test_argument_appending(self):
        stdout = StringIO()
        yield core.run(
            arguments=["1", "2", "3"], command=["echo"], stdout=stdout,
        )
        self.assertEqual(
            sorted(stdout.getvalue().splitlines()), ["1", "2", "3"],
        )


class TestFormatCommand(TestCase):
    def test_format_sections_are_replaced_with_the_argument(self):
        self.assertEqual(
            core.format_command(["hello", "{}.bar", "world"], argument="1"),
            ["hello", "1.bar", "world"],
        )

    def test_format_section_can_split_extensions_off(self):
        self.assertEqual(
            core.format_command(["foo", "{}", "{.}.mp3"], argument="2.mp4"),
            ["foo", "2.mp4", "2.mp3"],
        )

    def test_if_there_are_no_format_sections_the_argument_is_appended(self):
        self.assertEqual(
            core.format_command(["hello"], argument="1"), ["hello", "1"],
        )
