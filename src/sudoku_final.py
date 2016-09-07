""" 
Sudoku Solver Algorithm by Allister Quinn. Last updated Jul 2015.

TERMINOLOGY
grid:               The main grid of the puzzle.
sub-grid:       	A sub-grid within the main grid.
square:         	A single square within the grid.
row:            	A whole row of squares within the main grid.
column:         	A whole column of squares within the main grid.
sub-row:        	A row of three squares in a sub-grid.
sub-column:     	A column of three squares in a sub-grid.
candidate:     	    A possible solution for a square.
solved:         	A square is solved when the correct value is filled.

For in-depth descriptions of the various sudoku solving techniques 
used in this program, visit:
http://www.paulspages.co.uk/sudoku/howtosolve/index.htm
This is the sole resource used to generate the techniques
found in this program.
"""

import itertools
import sys

# Set puzzle dimensions. Grid length, sub-grid length, sub-grid height
grid_l = 9 # sys.argv[2]
sub_l = 3 # sys.argv[3]
sub_h = 3 # sys.argv[4]

# Holds puzzle itself as 2d list. Blank squares represented as 0.
# Individual square access: m_grid[x][y]
m_grid = [[] for x in range(grid_l)]

# Holds all possible candidates for each square as a 2d list of sets.
# Individual square set access: c_grid[x][y]
c_grid = [[set() for y in range(grid_l)] for x in range(grid_l)]

# Holds all solved values in an individual row/col/sub-grid
col_set = [set() for x in range(grid_l)]  # Access: col_set[x]
row_set = [set() for x in range(grid_l)]  # Access: row_set[y]
s_grid_set = [[set() for y in range(sub_l)] for x in range(sub_h)]
full_set = {y for y in range(1, grid_l + 1)}

def init():
    """Fill m_grid, c_grid, row/col/block sets from data file"""
    with open("../puzzles/" + "extreme1.txt") as puzzle: # open(sys.argv[1])
        for y in range(grid_l):
            line = puzzle.readline()
            for x in range(grid_l):
                m_grid[x].append(int(line[x]))
                if line[x] != '0': # square contains solution, add to sets
                    col_set[x].add(int(line[x]))
                    row_set[y].add(int(line[x]))
                    s_grid_set[x // sub_l][y // sub_h].add(int(line[x]))

        # Using row, col and subgrid sets, determine candidate sets for each square
        for y in range(grid_l):
            for x in range(grid_l):
                if m_grid[x][y] == 0:
                    solved_set = row_set[y] | col_set[x] | s_grid_set[x // sub_l][y // sub_h]
                    c_grid[x][y] = full_set - solved_set


def print_m_grid():
    """Print the main sudoku grid"""
    for y in range(grid_l):
        for x in range(grid_l):
            print(m_grid[x][y], end="")
            if x % sub_l == (sub_l - 1):
                print(" ", end="")
        print("")
        if y % sub_h == (sub_h - 1):
            print()


def is_solved():
    """Test if solved"""
    for x in range(grid_l):
        for y in range(grid_l):
            if len(c_grid[x][y]) != 0:
                return False
    return True


def write_solution(y):
    """Fill squares with only one candidate."""
    for x in range(grid_l):
        if len(c_grid[x][y]) == 1:
            solution = c_grid[x][y].pop()
            s_grid_x = (x // sub_l) * sub_l
            s_grid_y = (y // sub_h) * sub_h
            m_grid[x][y] = solution
            c_grid[x][y].clear()

            # Remove solution val from appropriate squares in candidate grid
            for c_y in range(s_grid_y, s_grid_y + sub_h):
                for c_x in range(s_grid_x, s_grid_x + sub_l):
                    c_grid[c_x][c_y].discard(solution)
            for i in range(grid_l):
                c_grid[x][i].discard(solution)
                c_grid[i][y].discard(solution)
    
def disjoint_subsets(x_range, y_range, n):
    """
    Finds a group of n squares in a row/col/subgrid where:
    - No squares contain more than n candidates each.
    - The cardinality of the set of all candidates in those squares is n.

    All candidates in that superset can be safely assumed to lie in those 
    squares, so the candidates can be removed from all other squares in that
    row/col/sg. This reduces potential candidates and helps us solve
    more squares. Expert Sudoku solvers may already know disjoint subsets 
    as "pairs" or "triples", where n is 2 and 3 respectively.

    Basic example: three squares in a particular row contain the candidate 
    sets {2,4}, {2,7} and {4,7} respectively. All three squares contain no
    more than three candidates, and the set of all candidates is {2,4,7},
    which has a cardinality of n - three. It can then be assumed that those
    squares MUST contain 2, 4 and 7 and nothing else. Any squares outside
    those three in the row can then have the candidates 2, 4 and 7 removed.
    """
    # Get all candidate sets in row/col/sg with cardinality n or less
    sets = []
    for y in range(y_range[0], y_range[1]):
        for x in range(x_range[0], x_range[1]):
            if 1 < len(c_grid[x][y]) <= n:
                sets.append(c_grid[x][y])

    # Goes through each combination of n sets in sets
    d_subsets = set()
    for combination in itertools.combinations(sets, n):
        superset = set()
        # Create superset of all candidates in n sets
        for c in combination:
            superset = superset | c
        if len(superset) == n:
            # If cardinality of superset is n, is disjoint subet.
            d_subsets.add(frozenset(superset))

    # For all disjoint subsets found, remove candidates from other squares
    for d in d_subsets:
        for y in range(y_range[0], y_range[1]):
            for x in range(x_range[0], x_range[1]):
                if not c_grid[x][y].issubset(d):
                    c_grid[x][y] = c_grid[x][y] - d


def iterator(func, *args):
    """Iterate function over each row, column and sub-grid"""
    # Iterate over row/col
    for sq in range(grid_l):
        func((0, grid_l), (sq, sq + 1), *args)
        func((sq, sq + 1), (0, grid_l), *args)

    # Iterate over subgrid
    for s_grid_y in range(sub_l):
        for s_grid_x in range(sub_h):
            func((s_grid_x * sub_l, s_grid_x * sub_l + sub_l), 
                 (s_grid_y * sub_h, s_grid_y * sub_h + sub_h), *args)


def main():
    """Runs solving techniques until puzzle solved or no possible solution."""
    init()
    for x in range(100):
        for i in range(grid_l):
            write_solution(i)
        for n in range(2, 5):
            iterator(disjoint_subsets, n)
        if(is_solved()):
            print_m_grid()
            break

main()
