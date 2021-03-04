from scanf import scanf

from solve import Solver

inputs = ()
with open("board.txt") as fin:
    inputs = [int(i) for i in fin.read().split()]

solver = Solver(inputs, debug=2)
res = solver.solve(depth = 5)

print(f"Best move: {res}")