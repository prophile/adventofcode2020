"""Solution to Day 5 of 2020 Advent of Code."""

from __future__ import annotations

import argparse
import dataclasses
import sys
from typing import IO, Iterable, Sequence


@dataclasses.dataclass(frozen=True, order=True)
class BoardingPassLocation:
    """A unique location of a boarding pass."""

    seat_id: int

    @property
    def row(self) -> int:
        """Get row number of this seat."""
        return self.seat_id >> 3

    @property
    def column(self) -> int:
        """Get column number of this seat."""
        return self.seat_id & 7

    @property
    def next(self) -> BoardingPassLocation:  # noqa: A003
        """Get next logical boarding pass location."""
        return self._offset(1)

    @property
    def previous(self) -> BoardingPassLocation:
        """Get previous logical boarding pass location."""
        return self._offset(-1)

    def _offset(self, offset: int) -> BoardingPassLocation:
        return type(self)(self.seat_id + offset)

    @classmethod
    def from_seat_id(self, seat_id: int) -> BoardingPassLocation:
        """Construct the boarding pass associated with a given seat ID."""
        return BoardingPassLocation(seat_id)

    @classmethod
    def from_seat_specification(cls, spec: str) -> BoardingPassLocation:
        """Construct the boarding pass associated with a seat specification."""
        binary_number = (
            spec.upper()
            .replace("F", "0")
            .replace("B", "1")
            .replace("L", "0")
            .replace("R", "1")
        )
        seat_id = int(binary_number, 2)
        return cls.from_seat_id(seat_id)

    @classmethod
    def enumerate_locations(
        cls,
        from_location: BoardingPassLocation,
        to_location: BoardingPassLocation,
    ) -> Iterable[BoardingPassLocation]:
        """Enumerate all possible locations in range."""
        for seat_id in range(from_location.seat_id, to_location.seat_id + 1):
            yield cls(seat_id)


def parse_boarding_passes(source: IO[str]) -> Iterable[BoardingPassLocation]:
    """Incrementally a file of boarding pass locations by their specifications."""
    for line in source:
        yield BoardingPassLocation.from_seat_specification(line.strip())


def argument_parser() -> argparse.ArgumentParser:
    """Generate parser for day5 arguments."""
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
        "-m",
        "--max-id",
        action="store_true",
        help="just find the max seat ID",
    )
    return parser


def main(
    args: Sequence[str] = sys.argv[1:],
) -> None:
    """Run as main entry point."""
    options = argument_parser().parse_args(args)

    boarding_passes = parse_boarding_passes(options.source)

    if options.max_id:
        print(max(x.seat_id for x in boarding_passes))
    else:
        # Construct set of all boarding pass locations
        locations = set(boarding_passes)
        first_location = min(locations)
        last_location = max(locations)
        for potential_location in BoardingPassLocation.enumerate_locations(
            first_location,
            last_location,
        ):
            if (
                potential_location not in locations
                and potential_location.previous in locations
                and potential_location.next in locations
            ):
                print(potential_location.seat_id)
                break
        else:
            print("No missing seat found", file=sys.stderr)
            raise SystemExit(1)


if __name__ == "__main__":
    main()
