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

if __name__ == '__main__':
    print(grid_l)

def printMessage():
    print("HIIIIIIIIIIIIIIIII")


### TESTS ###

