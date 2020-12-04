"""Solution to Day 4 of 2020 Advent of Code."""

import argparse
import enum
import re
import sys
from typing import IO, Callable, Dict, Iterable, List, Mapping, Sequence


class PassportField(enum.Enum):
    """Identifier for a particular passport field."""

    BIRTH_YEAR = "byr"
    ISSUE_YEAR = "iyr"
    EXPIRATION_YEAR = "eyr"
    HEIGHT = "hgt"
    HAIR_COLOUR = "hcl"
    EYE_COLOUR = "ecl"
    PASSPORT_ID = "pid"
    COUNTRY_ID = "cid"


OPTIONAL_FIELDS = {PassportField.COUNTRY_ID}


PassportRecord = Mapping[PassportField, str]


def parse_passport_records(source: IO[str]) -> Iterable[PassportRecord]:
    """Iteratively parse passport records from a file."""  # noqa: D401
    # The initial adverb is tricking flake8 into thinking the above line is
    # not imperative.
    current_record_contents: Dict[PassportField, str] = {}

    for line in source:
        components = line.split(" ")
        components = [x.strip() for x in components]
        components = [x for x in components if x]

        if not components:
            # Process this record
            if current_record_contents:
                yield current_record_contents
                current_record_contents = {}
            continue

        for component in components:
            component = component.strip()
            if not component:
                continue
            field_name, field_value = component.split(":", 1)
            try:
                true_field = PassportField(field_name)
            except ValueError:
                # Accept invalid data
                continue
            current_record_contents[true_field] = field_value

    # Emit the last record
    if current_record_contents:
        yield current_record_contents


Validator = Callable[[str], None]

VALIDATORS: Dict[PassportField, List[Validator]] = {x: [] for x in PassportField}


def validator(field: PassportField) -> Callable[[Validator], Validator]:
    """
    Add a validator for a given field.

    Usage is recommended as a decorator:

    ```
    @validator(PassportField.XXX)
    def validate_xxx(value: str) -> None:
        ...
    ```
    """

    def _wrap(fn: Validator) -> Validator:
        VALIDATORS[field].append(fn)
        return fn

    return _wrap


@validator(PassportField.BIRTH_YEAR)
def validate_birth_year(birth_year: str) -> None:
    """Validate birth year field."""
    if not 1920 <= int(birth_year) <= 2002:
        raise ValueError("Birth year is outside permissible range")


@validator(PassportField.ISSUE_YEAR)
def validate_issue_year(issue_year: str) -> None:
    """Validate issue year field."""
    if not 2010 <= int(issue_year) <= 2020:
        raise ValueError("Issue year is outside permissible range")


@validator(PassportField.EXPIRATION_YEAR)
def validate_expiration_year(expiration_year: str) -> None:
    """Validate expiration year field."""
    if not 2020 <= int(expiration_year) <= 2030:
        raise ValueError("Expiration year is outside permissible range")


@validator(PassportField.HEIGHT)
def validate_height(height: str) -> None:
    """Validate height field."""
    if height.endswith("cm"):
        height_cm = int(height.removesuffix("cm"))
        if not 150 <= height_cm <= 193:
            raise ValueError("Height (cm) is outside permissible range")
    elif height.endswith("in"):
        # Are inches ever truly valid to use?
        height_in = int(height.removesuffix("in"))
        if not 59 <= height_in <= 76:
            raise ValueError("Height (in) is outside permissible range")
    else:
        # Eugh
        raise ValueError("Height must be denoted in inches or cm")


RE_HCL = re.compile(r"^#[0-9a-f]{6}$")


@validator(PassportField.HAIR_COLOUR)
def validate_hair_colour(hair_colour: str) -> None:
    """Validate hair colour field."""
    if RE_HCL.match(hair_colour) is None:
        raise ValueError("Hair colour is not specified as a hex colour")


@validator(PassportField.EYE_COLOUR)
def validate_eye_colour(eye_colour: str) -> None:
    """Validate eye colour field."""
    if eye_colour not in ("amb", "blu", "brn", "gry", "grn", "hzl", "oth"):
        raise ValueError("Eye colour is not a recognised colour")


RE_PID = re.compile(r"^[0-9]{9}$")


@validator(PassportField.PASSPORT_ID)
def validate_passport_id(passport_id: str) -> None:
    """Validate passport ID field."""
    if RE_PID.match(passport_id) is None:
        raise ValueError("Passport ID is not nine decimal digits")


def validate_passport(
    passport_record: PassportRecord,
    permissive: bool,
) -> None:
    """
    Validate all fields of the passport.

    Raises a ValueError for any issues.
    """
    for required_key in PassportField:
        if required_key in passport_record:
            if not permissive:
                for validator in VALIDATORS[required_key]:
                    validator(passport_record[required_key])

        else:
            if required_key not in OPTIONAL_FIELDS:
                raise ValueError(f"Missing required field: {required_key}")


def argument_parser() -> argparse.ArgumentParser:
    """Generate parser for day4 arguments."""
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
        "-p",
        "--permissive",
        action="store_true",
        help="allow permissive validation (just checking presence)",
    )
    return parser


def main(
    args: Sequence[str] = sys.argv[1:],
) -> None:
    """Run as main entry point."""
    options = argument_parser().parse_args(args)

    valid_passports = 0

    for record in parse_passport_records(options.source):
        if options.verbose:
            print(record, file=sys.stderr)
        try:
            validate_passport(record, permissive=options.permissive)
        except ValueError as exc:
            if options.verbose:
                print(str(exc), file=sys.stderr)
        else:
            valid_passports += 1

    print(valid_passports)


if __name__ == "__main__":
    main()
