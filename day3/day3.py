"""Solution to Day 3 of 2020 Advent of Code."""

from __future__ import annotations

import argparse
import math
import re
import sys
from enum import Enum
from itertools import cycle
from typing import IO, Iterable, List, MutableSet, Sequence, Tuple


class DownhillSlope:
    """A map of a downhill slope with trees at integer coördinates."""

    def __init__(
        self,
        width: int,
        height: int,
        offset_x: int,
        offset_y: int,
        tree_set: MutableSet[Tuple[int, int]],
    ) -> None:
        """
        Construct directly from parameters.

        The `offset` components are used to offset indexes into the tree set.
        This is used to support the translate functionality.
        """
        self.width = width
        self.height = height
        self.offset_x = offset_x
        self.offset_y = offset_y
        self._trees = tree_set

    @classmethod
    def from_blank(cls, width: int, height: int) -> DownhillSlope:
        """Build a blank map."""
        return cls(width, height, 0, 0, set())

    @classmethod
    def from_text(cls, text: str) -> DownhillSlope:
        """Build a map from the reference text encoding."""
        lines = text.splitlines()
        height = len(lines)
        width = max(len(x) for x in lines)
        slope = cls.from_blank(width, height)
        for y, line in enumerate(lines):
            for x, character in enumerate(line):
                if character == "#":
                    slope.place_tree(x, y)
        return slope

    @classmethod
    def from_file(cls, file: IO[str]) -> DownhillSlope:
        """Build a map from text in a file."""
        return cls.from_text(file.read())

    def _normalise_coördinates(self, x: int, y: int) -> Tuple[int, int]:
        """Validate coördinates, wrap x, and apply offsets."""
        if y > self.height:
            # We permit y=height for 'bottoming out'
            raise ValueError(
                f"y={y} is further downhill than this map's height {self.height}",
            )
        if y < 0:
            raise ValueError(f"y={y} is further uphill than this map")
        x += self.offset_x
        y += self.offset_y
        return x % self.width, y

    def place_tree(self, x: int, y: int) -> None:
        """
        Add a tree at a given location.

        This is by construction idempotent: adding a tree to the same location
        multiple times has the same effect as doing so once.
        """
        true_x, true_y = self._normalise_coördinates(x, y)
        self._trees.add((true_x, true_y))

    def has_tree(self, x: int, y: int) -> bool:
        """Detect the presence of a tree at a given location."""
        true_x, true_y = self._normalise_coördinates(x, y)
        return (true_x, true_y) in self._trees

    def at_bottom(self) -> bool:
        """
        Check if this slope has bottomed-out.

        That is: is the height zero?
        """
        return self.height <= 0

    def translate(self, x: int, y: int) -> DownhillSlope:
        """Build a new slope offset by a given amount."""
        if y < 0:
            raise ValueError("cannot move uphill")
        return DownhillSlope(
            width=self.width,
            height=self.height - y,
            offset_x=self.offset_x + x,
            offset_y=self.offset_y + y,
            tree_set=self._trees,
        )


class TraversalDirection(Enum):
    """A direction in which one might traverse an integer slope."""

    LEFT = (-1, 0)
    RIGHT = (1, 0)
    DOWN = (0, 1)


Move = Iterable[TraversalDirection]
Path = Iterable[Move]


def count_trees(slope: DownhillSlope, path: Path) -> int:
    """Count the number of trees met traversing a slope in a given path."""
    full_path = cycle(path)
    num_trees = 0

    for move in full_path:
        if slope.at_bottom():
            break
        if slope.has_tree(0, 0):
            num_trees += 1
        for traversal in move:
            x, y = traversal.value
            slope = slope.translate(x, y)

    return num_trees


MOVE_RE = re.compile(r"([rldRLD])(\d*)")


def parse_move(move_description: str) -> Move:
    """
    Parse a move description.

    Move descriptions are given as the letters 'r', 'l', and 'd'. They may
    also have a number specified, such as 'r3', which gives a number of times
    to make the move.
    """
    move: List[TraversalDirection] = []

    for match in MOVE_RE.finditer(move_description):
        direction = {
            "r": TraversalDirection.RIGHT,
            "l": TraversalDirection.LEFT,
            "d": TraversalDirection.DOWN,
        }[match.group(1).lower()]
        if match.group(2):
            count = int(match.group(2))
        else:
            count = 1
        for _ in range(count):
            move.append(direction)

    return move


def argument_parser() -> argparse.ArgumentParser:
    """Generate parser for day3 arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source",
        type=argparse.FileType("r"),
    )
    parser.add_argument(
        "--route",
        type=str,
        dest="routes",
        action="append",
        default=None,
        help="routes to explore",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="say many things, some of them true",
    )
    return parser


DEFAULT_ROUTES = ["r3d1"]


def main(
    args: Sequence[str] = sys.argv[1:],
) -> None:
    """Run as main entry point."""
    options = argument_parser().parse_args(args)
    slope = DownhillSlope.from_file(options.source)

    tree_counts: List[int] = []

    routes = options.routes if options.routes is not None else DEFAULT_ROUTES

    for route_description in routes:
        move = parse_move(route_description)
        path = [move]
        num_trees = count_trees(slope, path)
        if options.verbose:
            print(f"{route_description}: {num_trees} trees", file=sys.stderr)
        tree_counts.append(num_trees)

    print(math.prod(tree_counts))


if __name__ == "__main__":
    main()
