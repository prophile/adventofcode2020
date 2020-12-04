"""Solution to Day 1 of 2020 Advent of Code."""

import argparse
import contextlib
import sys
from math import ceil, prod
from typing import IO, List, Optional, Sequence

Expense = int
ExpenseReport = Sequence[Expense]


def argument_parser() -> argparse.ArgumentParser:
    """Generate parser for day1 arguments."""
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
        "--components",
        type=int,
        help="number of separate entries to seek",
        default=2,
    )
    parser.add_argument(
        "--total",
        type=int,
        help="total to seek from the combined entries",
        default=2020,
    )
    return parser


def parse_expense_report(source: IO[str]) -> ExpenseReport:
    """Parse an expense report from a file."""
    report: List[int] = []
    for line in source:
        with contextlib.suppress(ValueError):
            report.append(int(line.strip()))
    report.sort()
    return report


def find_entries_with_sum(
    report: ExpenseReport,
    n: int,
    total: Expense,
) -> Optional[Sequence[Expense]]:
    """Find, if any, a subset of n entries summing to `total`."""
    if n == 0:
        return [] if total == 0 else None
    else:
        absolute_maximum = ceil(total / n)
        for index in range(len(report) - n + 1):
            value_at_index = report[index]
            if value_at_index > absolute_maximum:
                break
            subsequence = find_entries_with_sum(
                report[index + 1 :],
                n - 1,
                total - value_at_index,
            )
            if subsequence is not None:
                return [value_at_index] + list(subsequence)
        return None


def main(
    args: Sequence[str] = sys.argv[1:],
) -> None:
    """Run as main entry point."""
    options = argument_parser().parse_args(args)

    report = parse_expense_report(options.source)
    subentries = find_entries_with_sum(report, options.components, options.total)

    if subentries is not None:
        if options.verbose:
            print(
                "Discovered entries: {}".format(", ".join(str(x) for x in subentries)),
                file=sys.stderr,
            )
        print(prod(subentries))
    else:
        print("Did not find a combination", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
