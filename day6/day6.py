"""Solution to Day 6 of 2020 Advent of Code."""

from __future__ import annotations

import argparse
import sys
from typing import IO, Collection, Iterable, MutableSet, NewType, Optional, Sequence

CustomsClass = NewType("CustomsClass", str)
CustomsSet = Collection[CustomsClass]


def parse_customs_sets(source: IO[str], union: bool = True) -> Iterable[CustomsSet]:
    """Incrementally a file of group customs."""
    customs_set: Optional[MutableSet[CustomsClass]] = None

    for line in source:
        line = line.strip()
        if line:
            new_classes = {CustomsClass(x) for x in line}
            if customs_set is None:
                customs_set = new_classes
            elif union:
                customs_set |= new_classes
            else:
                customs_set &= new_classes
        else:
            if customs_set is not None:
                yield customs_set
                customs_set = None

    if customs_set is not None:
        yield customs_set


def argument_parser() -> argparse.ArgumentParser:
    """Generate parser for day6 arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source",
        type=argparse.FileType("r"),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="be verbose in output",
    )
    parser.add_argument(
        "-u",
        "--union",
        action="store_true",
        help="union the customs lines together",
    )
    return parser


def main(
    args: Sequence[str] = sys.argv[1:],
) -> None:
    """Run as main entry point."""
    options = argument_parser().parse_args(args)

    customs_sets = parse_customs_sets(options.source, union=options.union)

    print(sum(len(x) for x in customs_sets))


if __name__ == "__main__":
    main()
