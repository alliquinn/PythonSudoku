""" 
Sudoku Solver Reasoning Algorithm.

TERMINOLOGY
grid:           The main 9x9 grid of the puzzle.
sub-grid:       A 3x3 sub-grid within the main grid.
square:         A single square within the grid.
row:            A whole row of squares within the main grid.
column:         A whole column of squares within the main grid.
sub-row:        A row of three squares in a sub-grid.
sub-column:     A column of three squares in a sub-grid.
candidate:      A possible solution for a square.
solved:         A square is solved when the correct value is filled.

For in-depth descriptions of the various sudoku solving techniques 
used in this program, visit:
http://www.paulspages.co.uk/sudoku/howtosolve/index.htm
This is the sole resource used to generate the techniques
found in this program.
"""

import itertools
import sys

size = 9

# Holds puzzle itself as 2d list. Blank squares represented as 0.
# Individual square access: main_grid[x][y]
main_grid = [[] for x in range(9)]

# Holds all possible candidates for each square as a 2d list of sets.
# Individual square set access: candidates_grid[x][y]
candidates_grid = [[set() for y in range(9)] for x in range(9)]

# Holds all solved values in an individual row/col/sub-grid
col_set = [set() for x in range(9)]  # Access: col_set[x]
row_set = [set() for x in range(9)]  # Access: row_set[y]
sub_grid_set = [[set() for y in range(3)] for x in range(3)]

# Misc sets used for solving techniques/optimisation
full_set = {1, 2, 3, 4, 5, 6, 7, 8, 9}
coordinates_set = {0, 1, 2, 3, 4, 5, 6, 7, 8}


def init():
    """Fill main_grid, candidates_grid, row/col/block sets from data file"""
    #with open(sys.argv[1]) as puzzle:
    with open("../puzzles/easy1.txt") as puzzle:
        for y in range(9):
            next_line = puzzle.readline()
            for x in range(9):
                main_grid[x].append(int(next_line[x]))
                if next_line[x] != '0':
                    col_set[x].add(int(next_line[x]))
                    row_set[y].add(int(next_line[x]))
                    sub_grid_set[x // 3][y // 3].add(int(next_line[x]))

        for y in range(9):
            for x in range(9):
                if main_grid[x][y] == 0:
                    candidate_set = set.union(row_set[y], col_set[x],
                                              sub_grid_set[x // 3][y // 3])
                    candidates_grid[x][y] = full_set.difference(candidate_set)


def iter_over_subgrids(func, *args):
    """Iterate a function over each square in a subgrid"""
    for sub_grid_y in range(3):
        for sub_grid_x in range(3):
            func(sub_grid_x, sub_grid_y, *args)


def iter_over_line(func, *args):
    """Iterate a function over each square in a line"""
    for square in range(9):
        func(square, *args)


def print_main_grid():
    """Print the main sudoku grid"""
    for y in range(9):
        for x in range(9):
            print(main_grid[x][y], end="")
            if x % 3 == 2:
                print(" ", end="")
        print("")


def print_candidates_grid():
    """Print candidate list for each square"""
    for y in range(9):
        for x in range(9):
            print(candidates_grid[x][y], " ", end="")
        print("")


def is_solved():
    """Test if solved"""
    for y in range(9):
        if len(row_set[y]) != 9:
            return False
    return True


def pencil_in(solution, x, y, func):
    """Write solution to main_grid, updates sets and tables."""
    sub_grid_x = x // 3
    sub_grid_y = y // 3
    main_grid[x][y] = solution
    row_set[y].add(solution)
    col_set[x].add(solution)
    sub_grid_set[sub_grid_x][sub_grid_y].add(solution)
    candidates_grid[x][y].clear()

    for sg_y in range(sub_grid_y * 3, sub_grid_y * 3 + 3):
        for sg_x in range(sub_grid_x * 3, sub_grid_x * 3 + 3):
            candidates_grid[sg_x][sg_y].discard(solution)
    for i in range(9):
        candidates_grid[x][i].discard(solution)
        candidates_grid[i][y].discard(solution)


def single_candidate_square(y):
    """Solves squares that have only one candidate."""
    for x in range(9):
        if len(candidates_grid[x][y]) == 1:
            pencil_in(candidates_grid[x][y].pop(), x, y,
                      single_candidate_square)


def single_sq_candidate_row(y):
    """Solves squares where candidate appears only once in a row."""
    for candidate in full_set.difference(row_set[y]):  # Skip solved values
        count = 0
        prev_x = 0
        for x in range(9):
            if candidate in candidates_grid[x][y]:
                count += 1
                prev_x = x
        if count == 1:
            pencil_in(candidate, prev_x, y, single_sq_candidate_row)


def single_sq_candidate_col(x):
    """As single_sq_candidate_row, for columns."""
    for candidate in full_set.difference(col_set[x]):  # Skip solved values
        count = 0
        prev_y = 0
        for y in range(9):
            if candidate in candidates_grid[x][y]:
                count += 1
                prev_y = y
        if count == 1:
            pencil_in(candidate, x, prev_y, single_sq_candidate_col)


def single_sq_candidate_subgrid(sub_grid_x, sub_grid_y):
    """As single_sq_candidate_row, for subgrids."""
    for candidate in full_set.difference(sub_grid_set[sub_grid_x][sub_grid_y]):
        count = 0
        prev_coords = [0, 0]
        for y in range(sub_grid_y * 3, sub_grid_y * 3 + 3):
            for x in range(sub_grid_x * 3, sub_grid_x * 3 + 3):
                if candidate in candidates_grid[x][y]:
                    count += 1
                    prev_coords[0] = x
                    prev_coords[1] = y
        if count == 1:
            pencil_in(candidate, prev_coords[0], prev_coords[1],
                      single_sq_candidate_subgrid)


def number_claiming_row(sub_grid_x, sub_grid_y):
    """
    Finds candidates in block that lie only on one subrow,
    removes candidates from rest of row.
    """
    # Get set of all candidates each subrow
    subrow_sets = [set(), set(), set()]
    for y in range(sub_grid_y * 3, sub_grid_y * 3 + 3):
        for x in range(sub_grid_x * 3, sub_grid_x * 3 + 3):
            subrow_sets[y % 3] = subrow_sets[y % 3].union(candidates_grid[x][y])

    # Get candidates which only appear in one subrow
    claimed = [subrow_sets[0].difference(subrow_sets[1], subrow_sets[2])]
    claimed.append(subrow_sets[1].difference(subrow_sets[0], subrow_sets[2]))
    claimed.append(subrow_sets[2].difference(subrow_sets[0], subrow_sets[1]))

    # Remove candidates from other subrows in parent row
    for sub_row in range(3):
        for claimant in set(claimed[sub_row]):
            for x in range(9):
                if x // 3 != sub_grid_x:
                    candidates_grid[x][sub_grid_y * 3 + sub_row].discard(claimant)


def number_claiming_col(sub_grid_x, sub_grid_y):
    """As number_claiming_row, but for columns"""
    # Get set of all candidates each subcolumn
    subcol_sets = [set(), set(), set()]
    for x in range(sub_grid_x * 3, sub_grid_x * 3 + 3):
        for y in range(sub_grid_y * 3, sub_grid_y * 3 + 3):
            subcol_sets[x % 3] = subcol_sets[x % 3].union(candidates_grid[x][y])

    # Get candidates which only appear in one subcolumn
    claimed = [subcol_sets[0].difference(subcol_sets[1], subcol_sets[2])]
    claimed.append(subcol_sets[1].difference(subcol_sets[0], subcol_sets[2]))
    claimed.append(subcol_sets[2].difference(subcol_sets[0], subcol_sets[1]))

    # Remove candidates from other subcolumns in parent column
    for sub_col in range(3):
        for claimant in set(claimed[sub_col]):
            for y in range(9):
                if y // 3 != sub_grid_y:
                    candidates_grid[sub_grid_x * 3 + sub_col][y].discard(claimant)

    
def disjoint_subsets_row(y, n):
    """
    Finds a group of n squares in a row where:
    - No squares contain more than n candidates each.
    - The cardinality of the set of all candidates in the squares is n.
    All candidates in that set can be assumed to lie in those squares,
    so the set of candidates can be removed from all other squares in
    that row. Sudoku solvers may already know disjoint subsets as "pairs"
    or "triples".
    Basic example: three squares in a row contain the candidate sets
    {2,4}, {2,7} and {4,7} respectively. All three squares contain no
    more than three candidates, and the set of all candidates is {2,4,7},
    which has a cardinality of three. It can then be assumed that those
    squares MUST contain 2, 4 and 7 and nothing else. Any squares outside
    those three in the row can then have the candidates 2, 4 and 7 removed.
    """
    sets = []
    # Get all candidate sets in row with cardinality no greater than n
    for x in range(9):
        if 1 < len(candidates_grid[x][y]) <= n:
            sets.append(candidates_grid[x][y])

    # For all disjoint subsets found, remove candidates from other squares
    for d in get_disjoint_subsets(sets, n):
        for x in range(9):
            if not candidates_grid[x][y].issubset(d):
                candidates_grid[x][y] = candidates_grid[x][y].difference(d)


def disjoint_subsets_col(x, n):
    """As disjoint_subsets_row, for columns."""
    sets = []
    # Get all candidate sets in row with cardinality no greater than n
    for y in range(9):
        if 1 < len(candidates_grid[x][y]) <= n:
            sets.append(candidates_grid[x][y])

    # For all disjoint subsets found, remove candidates from other squares
    for d in get_disjoint_subsets(sets, n):
        for y in range(9):
            if not candidates_grid[x][y].issubset(d):
                candidates_grid[x][y] = candidates_grid[x][y].difference(d)


def disjoint_subsets_subgrid(sub_grid_x, sub_grid_y, n):
    """As disjoint_subsets_row, for sub-grids."""
    sets = []
    # Get all candidate sets in row with cardinality no greater than n
    for y in range(sub_grid_y * 3, sub_grid_y * 3 + 3):
        for x in range(sub_grid_x * 3, sub_grid_x * 3 + 3):
            if 1 < len(candidates_grid[x][y]) <= n:
                sets.append(candidates_grid[x][y])

    # For all disjoint subsets found, remove candidates from other squares
    for d in get_disjoint_subsets(sets, n):
        for y in range(sub_grid_y * 3, sub_grid_y * 3 + 3):
            for x in range(sub_grid_x * 3, sub_grid_x * 3 + 3):
                if not candidates_grid[x][y].issubset(d):
                    candidates_grid[x][y] = candidates_grid[x][y].difference(d)


def get_disjoint_subsets(sets, n):
    disjoint_subsets = set()
    # For each combination of n sets in sets
    for combination in itertools.combinations(sets, n):
        superset = set()
        # For each individual set in combination
        for c in combination:
            superset = superset.union(c)
        if len(superset) == n:
            # Cardinality of candidate superset in combination is n, is djss.
            disjoint_subsets.add(frozenset(superset))
    return disjoint_subsets


def solve():
    """Runs solving techniques until puzzle solved or no possible solution."""
    for x in range(100):
        iter_over_line(single_candidate_square)
        iter_over_line(single_sq_candidate_row)
        iter_over_line(single_sq_candidate_col)
        iter_over_subgrids(single_sq_candidate_subgrid)
        iter_over_subgrids(number_claiming_row)
        iter_over_subgrids(number_claiming_col)
        for n in range(2, 5):
            iter_over_line(disjoint_subsets_row, n)
            iter_over_line(disjoint_subsets_col, n)
            iter_over_subgrids(disjoint_subsets_subgrid, n)
        if is_solved() == 1:
            print_main_grid()
            break

init()
solve()