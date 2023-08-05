import multiprocessing
import re
import sys

from twisted.internet import defer, protocol, reactor
from twisted.internet.task import coiterate
from twisted.python.procutils import which


class VergeProcess(protocol.ProcessProtocol):
    def __init__(self, stdout, stderr=sys.stderr, reactor=reactor):
        self.done = defer.Deferred()
        self.reactor = reactor
        self.stdout = stdout
        self.stderr = stderr

    @classmethod
    def spawn(cls, command, *args, **kwargs):
        protocol = cls(*args, **kwargs)
        protocol.reactor.spawnProcess(
            processProtocol=protocol,
            executable=which(command[0])[0],
            args=command,
        )
        return protocol.done

    def errReceived(self, data):
        self.stderr.write(data)

    def outReceived(self, data):
        self.stdout.write(data)

    def processEnded(self, reason):
        self.done.callback(None)


def run(command, arguments, max_processes=None, stdout=sys.stdout):
    if max_processes is None:
        max_processes = multiprocessing.cpu_count()

    processes = (
        VergeProcess.spawn(format_command(command, argument), stdout=stdout)
        for argument in arguments
    )

    return defer.gatherResults(
        coiterate(processes) for _ in xrange(max_processes)
    )


def format_command(command, argument):
    formatted, matches = [], 0
    for arg in command:
        arg, subs_made = re.subn(r"\{(.*)\}", _special_format(argument), arg)
        formatted.append(arg)
        matches += subs_made

    if not matches:
        formatted.append(argument)

    return formatted


def _special_format(argument):
    def replace(match):
        format = match.group(1)
        if not format:
            return argument
        elif format == ".":
            return argument.partition(".")[0]
    return replace
