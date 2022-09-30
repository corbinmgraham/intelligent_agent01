import os
import sys
import time
import argparse as ap
import random as r
import threading

# search algorithms
from search import *

# board (from input)
board = []

single_use_result = None

# list of algorithms available
algorithms = {
    "bfs": breadth_first_graph_search,
    "ids": iterative_deepening_search,
    "h1": astar_search_h1,
    "h2": astar_search_h2,
    "h3": astar_search_h3
}

# print out board at current state
def print_board():
    for i in board:
        print(*i, end=" ")
        print()

def get_order():
    return (board[0][0], board[0][1], board[0][2],
            board[1][0], board[1][1], board[1][2],
            board[2][0], board[2][1], board[2][2])

def gen_puzzle():
    puzzle = EightPuzzle(get_order())
    puzzle.solve = puzzle.check_solvability(get_order())
    return puzzle

# open file and initialize board
def get_file(name):
    try:
        with open(name, "r") as f:
            for line in f:
                board.append(line.split())  
    except:
        print(f"{name} could not be opened.")
        sys.exit(1)

    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == "_":
                board[i][j] = "0"
            board[i][j] = int(board[i][j])

    return f"{name}"

# run specified algorithm
def get_algorithm(name):
    if name in algorithms:
        global algorithm ; algorithm = algorithms[name]
        return name
    else:
        print(f"unable to find algorithm \'{name}\', generating random.")
        return rand_algo()

# generate a random algorithm
def rand_algo():
    return get_algorithm(r.choice(list(algorithms.keys())))

def run_all_algorithms(file_open):
    printables = []
    print(file_open)
    for algo in algorithms:
        get_algorithm(algo)
        puzzle = gen_puzzle()

        if not puzzle.solve:
            print("The inputted puzzle is not solvable:")
            print_board()
            break

        print(f"Starting {algo} on {file_open}")

        result = get_result(puzzle)

        print_sol = printable_solution(result)
        print_sol.insert(0, "File: " + file_open)
        print_sol.insert(1, ("Algorithm: " + algo))
        printables.append(print_sol)
        print("Completed ", algo)
    return printables

# parse argv
def init_parse():
    parser = ap.ArgumentParser(
    description="Solve 8-Puzzle using various algorithms")
    parser.add_argument(
        "-f", "--fPath", dest="path", help="file path")
    parser.add_argument(
        "-dp", "--dPath", dest="dPath", help="directory path")
    parser.add_argument(
        "-a", "--alg", dest="alg", help="algorithm")
    parser.add_argument(
        "-d", "--display", const=True, default=False, nargs="?", help="display each state")
    args = parser.parse_args()
    return args

# handle the command line arguments
def handle_args():
    args = init_parse()
    print_statements = []
    if len(sys.argv) > 1:
        if args.dPath:
            printables = []
            ### input all files from directory
            ### run all algorithms on each file adding it to a final state then print to file
            print(args.dPath)
            for filename in os.listdir(args.dPath):
                f = os.path.join(args.dPath, filename)
                printables.append(run_all_algorithms(get_file(f)))
            print_solution_to_file(printables, ("solutions.txt"))
            sys.exit(0)
        if args.path:
            print_statements.append("File:" + get_file(args.path))
        else:
            print("No file path given, exiting.")
            sys.exit(1)
        if args.alg:
            print_statements.append("Algorithm:" + get_algorithm(str.lower(args.alg)))
        else:
            print("Choosing Random Algorithm: ", rand_algo())
        if args.display:
            print(*print_statements, end="\n")
            return True
    else:
        print("Not enough arguments provided.\n\nGenerating random scenario:")
    return False

def timeout_data():
    result = EightPuzzle
    result.time = 1000
    result.nodes = "<<?>>"
    result.paths = "Timed out."
    result.print_path = "Timed out."
    return result

# timeout for running algorithm
def timeout_func():
    i = 0
    while True:
        if i >= 900: break
        time.sleep(1)
        i += 1

    global single_use_result
    single_use_result = False

def single_use_func(puzzle):
    # set the global variable
    global single_use_result
    single_use_result = algorithm(puzzle)
    return single_use_result

def bf_timeout(puzzle):
    # create thread for timer and if the timer ends and there is no global result, then return timeout data
    ft = threading.Thread(target=single_use_func, args=(puzzle,))
    ft.setDaemon(True)
    ft.start()
    tt = threading.Thread(target=timeout_func)
    tt.setDaemon(True)
    tt.start()
    while True:
        if single_use_result is False:
            return None
        elif single_use_result is not None:
            return single_use_result

# get the result of an algorithm
def get_result(puzzle):
    start = time.perf_counter()
    result = bf_timeout(puzzle)
    stop = time.perf_counter()
    if (result is None) or (result is False):
        return result
    
    result.print_sol = result.solution()
    result.time = (stop-start)
    result.nodes = len(pnodes)
    pnodes.clear()
    result.paths = len(result.print_sol)
    result.print_path = ""
    for i in result.print_sol:
        result.print_path = result.print_path + i[0]
    
    return result

# generate a printable solution
def printable_solution(result):
    if result is False or result is None:
        return printable_solution(timeout_data())
    the_solution = []
    mic, sec = math.modf(result.time)
    mic = str(mic).split('.')[1]

    the_solution.append(f"Total nodes generated: {result.nodes}")
    the_solution.append(f"Total time taken: {int(sec)} sec {mic[:6]} microSec."
        if result.time < 999 else "Total time taken: >15 min")
    the_solution.append(f"Path length: {result.paths}")
    the_solution.append(f"Path: {result.print_path}")
    return the_solution

def print_solution_to_file(files, name):
    with open("solutions.txt", "w") as f:
        for results in files:
            for result in results:
                print(*result, sep="\n", file=f)
                print(file=f)
            # print to file **
    print("Files printed to \'solutions.txt\'.")

def print_solution_to_screen(result):
    print(*result, sep="\n")

# main
def main():
    init_parse()
    display = handle_args()

    if display == True:
        print("Before:")
        print_board()

    puzzle = gen_puzzle()

    if not puzzle.solve:
        print("The inputted puzzle is not solvable:")
        print_board()
        sys.exit(1)

    result = get_result(puzzle)

    if display == True:
        i = 0
        for s in path_states(result):
            print(board8(s))
            i += 1
        print("Total moves to result:", i)
        
    print_solution_to_screen(printable_solution(result))

    sys.exit(0)

if __name__ == "__main__":
    main()