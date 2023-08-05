import argparse
import sys


def parse(argv=None, stdin=sys.stdin):
    if argv is None:
        argv = sys.argv[1:]

    argv, original_argv, parallelized_arguments = [], iter(argv), []
    for arg in original_argv:
        if arg == ":::":
            parallelized_arguments.extend(original_argv)
        else:
            argv.append(arg)

    if not parallelized_arguments:
        parallelized_arguments = (line[:-1] for line in stdin)

    return dict(
        vars(parser.parse_args(argv)), arguments=parallelized_arguments,
    )


parser = argparse.ArgumentParser()
parser.add_argument("command", nargs=argparse.REMAINDER)
