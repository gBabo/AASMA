import random
from dataclasses import dataclass, field
from enum import Enum
from typing import List
from tile import *


class Direction(Enum):
    North = 1
    South = 2
    East = 3
    West = 4


@dataclass
class Wind:
    direction: Direction
    strength: int = 10  # Max Intensity


@dataclass(order=True, repr=True)
class Wildfire:
    wid: int
    start_location: Point = field(compare=False)
    start_time: int = field(default=1, compare=False)
    tiles: List[Tile] = field(default_factory=list, compare=False)

    def add_fire(self, tile: Tile):
        self.tiles.append(tile)

    def fire_spread(self):
        return len(self.tiles) - 1


def update_wildfire(wild: Wildfire) -> None:
    for tile in wild.tiles:
        decreased = tile.integrity - tile.fire_intensity
        tile.integrity = (MIN_INTEGRITY, decreased)[decreased > MIN_INTEGRITY]

        if tile.integrity == 0:
            decreased = tile.fire_intensity - DECAY
            tile.fire_intensity = (MIN_FIRE, decreased)[decreased > MIN_FIRE]
        elif decreased > 0 and tile.fire_intensity < MAX_FIRE:
            tile.fire_intensity += 1

        if tile.fire_intensity <= 0:
            tile.on_fire = False
    wild.tiles = [tile for tile in wild.tiles if tile.on_fire]


def expand_wildfire(wild: Wildfire, tile_dict: dict, wind: Wind) -> None:
    wild.start_time += 1
    direct = [Direction.North, Direction.South, Direction.East, Direction.West] \
             + (wind.strength - 1) * [wind.direction]
    types = [Population, Forest, Road]
    new_tiles = []

    for tile in wild.tiles:
        if random.randint(1, 10) <= tile.fire_intensity:
            choice = random.choice(direct)
            if choice == Direction.North:
                if tile.point.y == 0:
                    continue
                new = tile_dict[Point(tile.point.x, tile.point.y - 1)]
            elif choice == Direction.South and tile.point.y:
                if tile.point.y == 31:
                    continue
                new = tile_dict[Point(tile.point.x, tile.point.y + 1)]
            elif choice == Direction.East and tile.point.x < 31:
                if tile.point.x == 31:
                    continue
                new = tile_dict[Point(tile.point.x + 1, tile.point.y)]
            else:
                if tile.point.x == 0:
                    continue
                new = tile_dict[Point(tile.point.x - 1, tile.point.y)]
            if new.__class__ == Water or new.on_fire or new.integrity == 0:
                continue
            if new.__class__ not in random.choices(types, weights=[0.3, 0.6, 0.1], k=1):
                continue
            new.fire_intensity = 1
            new.on_fire = True
            new_tiles.append(new)

    for fire in new_tiles:
        wild.add_fire(fire)
