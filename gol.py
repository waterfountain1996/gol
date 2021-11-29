import argparse
import os
import time
from urllib.request import urlopen
from urllib.error import HTTPError
from typing import Optional


BASE_URL = "https://www.conwaylife.com/patterns/{}.cells"


def find_pattern(name: str) -> Optional[str]:
    """
    Find pattern by name on conwaylife.com/wiki.
    """
    try:
        resp = urlopen(BASE_URL.format(name.lower()))
    except HTTPError:
        return

    return "\n".join(
        s for s in resp.read().decode().split("\n")
        if not s.startswith("!")
    )


def parse_pattern(pattern: str) -> set[tuple[int, int]]:
    """
    Parse .cells pattern file.
    """
    cells = []
    for i, line in enumerate(pattern.split("\n")):
        cells.extend((i, j) for j, c in enumerate(line) if c == "O")
    return set(cells)


def get_pattern(name: str) -> Optional[set[tuple[int, int]]]:
    """
    Find and parse a pattern
    """
    if (pattern := find_pattern(name)):
        return parse_pattern(pattern)


def clear_board():
    """
    Clear the screen.
    """
    os.system("clear")


def draw_board(
    size: tuple[int, int],
    cells: set[tuple[int, int]],
    *,
    alive: str = "+",
    dead: str = " ",
):
    """
    Draw cell board.

    Args:
        size: size of the board.
        cells: alive cells.
        alive: character to represent a living cell.
        dead: character to represent a dead cell.
    """
    drawn = 0
    for i in range(size[0]):
        # Get cells that are on the current row.
        cs = {c[1] for c in cells if c[0] == i}
        drawn += len(cs)
        row = ''.join(alive if i in cs else dead for i in range(size[1]))
        print(row)
    return drawn


def neigbours(cell: tuple[int, int]):
    """Generator function to get all the neigbours of the given cell."""
    x, y = cell
    yield x + 1, y
    yield x + 1, y + 1
    yield x, y + 1
    yield x - 1, y + 1
    yield x - 1, y
    yield x - 1, y - 1
    yield x, y -1
    yield x + 1, y  -1


def get_all_cells(cells: set[tuple[int, int]]) -> set[tuple[int, int]]:
    """
    Get all participating in the game.

    It includes both alive and dead neigbours of currently living cells.

    Args:
        cells: current set of living cells
    """
    all_cells = cells.copy()
    for c in cells:
        ns = set(neigbours(c))
        all_cells |= ns

    return all_cells


def game(
    size: tuple[int, int],
    cells: set[tuple[int, int]],
    period: float = 0.25,
    generations: int = None,
    alive: str = "+",
    dead: str = " ",
):
    """
    Run the Game of Life.

    Args:
        size: size of the board
        cells: intial pattern
        period: time between generations
        generations: number of periods to play. None for infinity.
        alive: character representing a living cell.
        dead: character representing a dead cell.
    """
    i = 1
    while True:
        clear_board()            
        if not (draw_board(size, cells, alive=alive, dead=dead)):
            break

        participants = get_all_cells(cells)

        ns = {c: len(set(neigbours(c)) & cells) for c in participants}

        living = {c for c in cells if ns[c] in (2, 3)}
        reborn = {c for c in participants if ns.get(c) == 3 and c not in cells}

        cells = living | reborn
        time.sleep(period)
    
        if generations and i == generations:
            break
        
        i += 1


parser = argparse.ArgumentParser()
parser.add_argument("-p", help="Initial pattern name", default="block")
parser.add_argument("-ww", type=int, help="Width of the board", default=10)
parser.add_argument("-hh", type=int, help="Height of the board", default=10)
parser.add_argument("-x", type=int, help="X axis offset", default=0)
parser.add_argument("-y", type=int, help="Y axis offset", default=0)
parser.add_argument("-d", type=float, help="Delay between generations", default=0.25)
parser.add_argument("-g", type=int, help="Generations to live")
parser.add_argument("--alive", help="Living cell character")
parser.add_argument("--dead", help="Dead cell character")


if __name__ == "__main__":
    try:
        args = parser.parse_args()
        if (pattern := get_pattern(args.p)):
            pattern = {(c[0] + args.y, c[1] + args.x) for c in pattern}
            game(
                (args.hh, args.ww),
                pattern,
                period=args.d,
                generations=args.g,
                alive=args.alive[0] if args.alive else "+",
                dead=args.dead[0] if args.dead else " ",
            )
        else:
            print(f"Could not find {args.p}")
    except KeyboardInterrupt:
        pass
