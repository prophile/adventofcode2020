"""Solution to Day 7 of 2020 Advent of Code."""

from __future__ import annotations

import argparse
import sys
from typing import (
    IO,
    DefaultDict,
    Dict,
    Iterable,
    List,
    Mapping,
    NewType,
    Optional,
    Sequence,
    Set,
    Tuple,
)

Colour = NewType("Colour", str)


class BagRuleset:
    """Set of rules about what bags can contain what."""

    def __init__(self) -> None:
        """Construct without any rules."""
        self._rules: Dict[Tuple[Colour, Colour], int] = {}
        self._transitive_paths: Optional[Mapping[Tuple[Colour, Colour], int]] = None

    def add_rule(self, container_type: Colour, contains: Mapping[Colour, int]) -> None:
        """Add a rule that a container contains some contents."""
        for contained_colour, count in contains.items():
            if count <= 0:
                continue
            self._rules[container_type, contained_colour] = count
        self._invalidate_caches()

    def _invalidate_caches(self) -> None:
        """Invalidate any transitive caches."""
        self._transitive_paths = None

    def all_colours(self) -> Iterable[Colour]:
        """Get all colours mentioned."""
        already_mentioned: Set[Colour] = set()
        for container, contained in self._rules.keys():
            if container not in already_mentioned:
                yield container
                already_mentioned.add(container)
            if contained not in already_mentioned:
                yield contained
                already_mentioned.add(contained)

    def can_transitively_contain(self, container: Colour, contained: Colour) -> bool:
        """Determine recursively whether a container can contain some contained colour."""
        transitive_paths = self._get_transitive_path_cache()
        return (container, contained) in transitive_paths

    def total_contained_transitively(self, container: Colour) -> int:
        transitive_paths = self._get_transitive_path_cache()
        return sum(transitive_paths.get((container, x), 0) for x in self.all_colours())

    def _get_transitive_path_cache(self) -> Mapping[Tuple[Colour, Colour], int]:
        if self._transitive_paths is None:
            transitive_paths = self._compile_transitive_path_cache()
            self._transitive_paths = transitive_paths
            return transitive_paths
        else:
            return self._transitive_paths

    def _compile_transitive_path_cache(self) -> Mapping[Tuple[Colour, Colour], int]:
        routes_from: Dict[Colour, List[Tuple[Colour, int]]]
        routes_from = {x: [] for x, _ in self._rules.keys()}
        for (x, y), z in self._rules.items():
            routes_from[x].append((y, z))

        worklist: List[Tuple[Colour, Colour, int]] = [
            (x, x, 1) for x in routes_from.keys()
        ]
        transitive_paths: DefaultDict[Tuple[Colour, Colour], int] = DefaultDict(int)

        while worklist:
            origin, via, count = worklist.pop()
            for successor, successor_count in routes_from.get(via, []):
                total_count = count * successor_count
                transitive_paths[origin, successor] += total_count
                worklist.append((origin, successor, total_count))

        return dict(transitive_paths)

    def __str__(self) -> str:
        """Display a useful debugging output."""
        return "<BagRuleset rules={0!r}>".format(self._rules)


def _add_rule_from_declaration(ruleset: BagRuleset, declaration: str) -> None:
    """Add the rule from a single rule declaration."""
    declaration = declaration.replace(".", "")

    container, contents = declaration.split(" contain ", 1)
    if contents == "no other bags":
        ruleset.add_rule(Colour(container), {})
        return

    items = contents.split(", ")
    rule_contents: Dict[Colour, int] = {}
    for item in items:
        count, description = item.split(" ", 1)
        if count == "no":
            count_int = 0
        else:
            count_int = int(count)
        if description.endswith("bag"):
            description += "s"
        rule_contents[Colour(description)] = count_int
    ruleset.add_rule(Colour(container), rule_contents)


def parse_bag_rules(src: IO[str]) -> BagRuleset:
    """Parse a file of rule declarations into a ruleset."""
    ruleset = BagRuleset()
    for line in src:
        _add_rule_from_declaration(ruleset, line.strip())
    return ruleset


def argument_parser() -> argparse.ArgumentParser:
    """Generate parser for day7 arguments."""
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
        "-t",
        "--total",
        action="store_true",
        help="show the number of downstream bags",
    )
    return parser


def main(
    args: Sequence[str] = sys.argv[1:],
) -> None:
    """Run as main entry point."""
    options = argument_parser().parse_args(args)

    rules = parse_bag_rules(options.source)

    contain_count = 0

    if options.total:
        print(rules.total_contained_transitively(Colour("shiny gold bags")))
    else:
        for colour in rules.all_colours():
            if rules.can_transitively_contain(colour, Colour("shiny gold bags")):
                if options.verbose:
                    print("Found container:", colour, file=sys.stderr)
                contain_count += 1

        print(contain_count)


if __name__ == "__main__":
    main()
