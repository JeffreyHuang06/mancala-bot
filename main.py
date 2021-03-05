from scanf import scanf
from solve import Solver, Solver_MT

inputs = ()
with open("board.txt") as fin:
    inputs = [int(i) for i in fin.read().split()]

def main():
    solver = Solver(inputs, debug=1)
    res = solver.solve(depth = 10)

    print(f"Best move: {res.best_move}")

if __name__ == "__main__":
    main()