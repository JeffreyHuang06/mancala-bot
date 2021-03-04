from scanf import scanf

from solve import Solver

inputs = ()
with open("board.txt") as fin:
    inputs = [int(i) for i in fin.read().split()]

solver = Solver(inputs)
res = solver.solve(depth = 5)

print(res)