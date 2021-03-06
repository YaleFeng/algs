## Solve Every Sudoku Puzzle

## See http://norvig.com/sudoku.html

## Throughout this program we have:
##   r is a row,    e.g. 'A'
##   c is a column, e.g. '3'
##   s is a square, e.g. 'A3'
##   d is a digit,  e.g. '9'
##   u is a unit,   e.g. ['A1','B1','C1','D1','E1','F1','G1','H1','I1']
##   grid is a grid,e.g. 81 non-blank chars, e.g. starting with '.18...7...
##   values is a dict of possible values, e.g. {'A1':'12349', 'A2':'8', ...}

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

digits   = '1234'
rows     = 'ABCD'
cols     = digits
squares  = cross(rows, cols)
unitlist = ([cross(rows, c) for c in cols] +
            [cross(r, cols) for r in rows] +
            [cross(rs, cs) for rs in ('AB','CD') for cs in ('12','34')])
units = dict((s, [u for u in unitlist if s in u])
             for s in squares)
peers = dict((s, set(sum(units[s],[]))-set([s]))
             for s in squares)

################ Unit Tests ################


def test():
    "A set of tests that must pass."
    assert len(squares) == 16
    assert len(unitlist) == 12
    assert all(len(units[s]) == 3 for s in squares)
    assert all(len(peers[s]) == 7 for s in squares)
    assert units['C2'] == [['A2', 'B2', 'C2', 'D2'],
                           ['C1', 'C2', 'C3', 'C4'],
                           ['C1', 'C2', 'D1', 'D2']]
    assert peers['C2'] == set(['A2', 'B2', 'D2', 
                               'C1', 'C3', 'C4',
                               'D1'])
    print('All tests pass.')

################ Parse a Grid ################

def parse_grid(grid):
    """Convert grid to a dict of possible values, {square: digits}, or
    return False if a contradiction is detected."""
    ## To start, every square can be any digit; then assign values from the grid.
    values = dict((s, digits) for s in squares)
    for s,d in grid_values(grid).items():
        print("\ns, d", s, d)
        if d in digits and not assign(values, s, d):
            return False ## (Fail if we can't assign d to square s.)
    return values

def grid_values(grid):
    "Convert grid into a dict of {square: char} with '0' or '.' for empties."
    chars = [c for c in grid if c in digits or c in '0.']
    if len(chars) != 16: print(grid, chars, len(chars))
    assert len(chars) == 16
    return dict(zip(squares, chars))

################ Constraint Propagation ################

def assign(values, s, d):
    """Eliminate all the other values (except d) from values[s] and propagate.
    Return values, except return False if a contradiction is detected."""
    print("  assign", d, "to cell",s," *** start")
    other_values = values[s].replace(d, '')
    if all(eliminate(values, s, d2) for d2 in other_values):
        print("  assign", d, "to cell",s," *** done")
        return values
    else:
        return False

def eliminate(values, s, d):
    """Eliminate d from values[s]; propagate when values or places <= 2.
    Return values, except return False if a contradiction is detected."""
    print("    eliminate", d, "from", s, "start")
    if d not in values[s]:
        return values ## Already eliminated
    values[s] = values[s].replace(d,'')
    ## (1) If a square s is reduced to one value d2, then eliminate d2 from the peers.
    if len(values[s]) == 0:
        return False ## Contradiction: removed last value
    elif len(values[s]) == 1:
        d2 = values[s]
        if not all(eliminate(values, s2, d2) for s2 in peers[s]):
            return False
    ## (2) If a unit u is reduced to only one place for a value d, then put it there.
    for u in units[s]:
        dplaces = [s for s in u if d in values[s]]
        if len(dplaces) == 0:
            return False ## Contradiction: no place for this value
        elif len(dplaces) == 1:
            # d can only be in one place in unit; assign it there
            if not assign(values, dplaces[0], d):
                return False
    print("    eliminate", d, "from", s, "finish")
    display(values)
    return values

################ Display as 2-D grid ################

def display(values):
    "Display these values as a 2-D grid."
    width = 1+max(len(values[s]) for s in squares)
    line = '+'.join(['-'*(width*2)]*2)
    print()
    for r in rows:
        print(''.join(values[r+c].center(width) + ('|' if c in '2' else '')
                      for c in cols))
        if r in 'B': print(line)
    print()

################ Search ################

def solve(grid): return search(parse_grid(grid))

def search(values):
    "Using depth-first search and propagation, try all possible values."
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in squares):
        return values ## Solved!
    ## Chose the unfilled square s with the fewest possibilities
    print("\nsearch\n")
    n,s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    for d in values[s]:
        result = search(assign(values.copy(), s, d))
        if result: return result

################ System test ################

import time

def solve_all(grids, name=''):
    """Attempt to solve a sequence of grids. Report results."""
    times, results = zip(*[time_solve(grid) for grid in grids])
    N = len(results)
    if N > 1:
        print("Solved %d of %d %s puzzles (avg %.2f secs (%d Hz), max %.2f secs)." % (
            sum(results), N, name, sum(times)/N, N/sum(times), max(times)))
            
def time_solve(grid):
    start = time.clock()
    values = solve(grid)
    t = time.clock()-start
    return (t, solved(values))

def solved(values):
    "A puzzle is solved if each unit is a permutation of the digits 1 to 9."
    def unitsolved(unit): return set(values[s] for s in unit) == set(digits)
    return values is not False and all(unitsolved(unit) for unit in unitlist)


#grid1  = '21..3.121.......'
#grid1  = '21..43121.......'
grid1  = '4.....2...4...1.'
#grid1  = '1.....2.......4.'

#test()
#display(parse_grid(grid1))
display(solve(grid1))
    
#if __name__ == '__main__':
    #test()
    #solve_all(open("sudoku-easy50.txt"), "easy")
    #solve_all(open("sudoku-top95.txt"), "hard")
    #solve_all(open("sudoku-hardest.txt"), "hardest")
