"""Solution to Day 2 of 2020 Advent of Code."""

import argparse
import collections
import dataclasses
import re
import sys
from typing import IO, Callable, Sequence


@dataclasses.dataclass(frozen=True)
class PasswordDatabaseEntry:
    """Entry in the 'password/rule' database."""

    argument_lhs: int
    argument_rhs: int
    character: str
    password: str


ValidityRule = Callable[[PasswordDatabaseEntry], bool]


def validity_rule_count(entry: PasswordDatabaseEntry) -> bool:
    """
    Determine if this password is valid by the first ruleset.

    This ruleset interprets the LHS and RHS as a minimum and maximum count, and
    validates that the character appears in the password at a number of times
    between those counts.
    """
    minimum, maximum = entry.argument_lhs, entry.argument_rhs
    return minimum <= collections.Counter(entry.password)[entry.character] <= maximum


def validity_rule_exactly_one(entry: PasswordDatabaseEntry) -> bool:
    """
    Determine if this password is valid by the second ruleset.

    This ruleset interprets the LHS and RHS as 1-indexed positions into the password,
    and validates that the character appears in exactly one of those positions.
    """
    position_left, position_right = entry.argument_lhs - 1, entry.argument_rhs - 1
    appears_left = entry.password[position_left] == entry.character
    appears_right = entry.password[position_right] == entry.character
    return appears_left ^ appears_right


VALIDITY_RULES = {
    "count": validity_rule_count,
    "exactly_one": validity_rule_exactly_one,
}
DEFAULT_VALIDITY_RULE = "count"


def argument_parser() -> argparse.ArgumentParser:
    """Generate parser for day2 arguments."""
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
        "--rule",
        help="choose which validity rule to use for the count",
        choices=VALIDITY_RULES.keys(),
        default=DEFAULT_VALIDITY_RULE,
    )
    return parser


ENTRY_RE = re.compile(r"^(\d+)-(\d+) (.): (.+)")


def parse_password_database(source: IO[str]) -> Sequence[PasswordDatabaseEntry]:
    """Parse a flat-file database of password/rule entries."""
    entries = []

    for line in source:
        line = line.strip()
        match = ENTRY_RE.match(line)
        if match is None:
            continue
        entries.append(
            PasswordDatabaseEntry(
                argument_lhs=int(match.group(1)),
                argument_rhs=int(match.group(2)),
                character=match.group(3),
                password=match.group(4),
            ),
        )

    return entries


def count_valid_entries(
    database: Sequence[PasswordDatabaseEntry],
    rule: ValidityRule,
) -> int:
    """Count the number of database entries matching a validity rule."""
    return sum(1 for entry in database if rule(entry))


def main(
    args: Sequence[str] = sys.argv[1:],
) -> None:
    """Run as main entry point."""
    options = argument_parser().parse_args(args)

    database = parse_password_database(options.source)
    rule = VALIDITY_RULES[options.rule]
    print(count_valid_entries(database, rule))


if __name__ == "__main__":
    main()
