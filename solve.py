import builtins
from os import stat
from typing import List

ListSizeError = Exception("List size must be even number")

def magic(inputs, val):
    inputs.append(val)
    return inputs

class Solver:
    def __init__(self, inputs: List[int]):
        self.mid, self.length, self.p1_range, self.p2_range, self.mids, self.inputs = Solver.resize_board(inputs)

        print("Solver initialized")

        print()
        print(f"mid: {self.mid}")
        print(f"length: {self.length}")
        print(f"p1_range: {self.p1_range}")
        print(f"p2_range: {self.p2_range}")
        print(f"inputs: {self.inputs}")
        print()
    
    @staticmethod
    def resize_board(board: List[int]):
        _length = len(board)
        if _length % 2: raise ListSizeError

        _mid = _length // 2
        _p1_range = range(1, _mid)
        _p2_range = range(_mid+1, _length)
        _mids = [0, _mid]

        _new_board = [board[0]] + board[1::2] + board[2::2][::-1]

        return [
            _mid,
            _length,
            _p1_range,
            _p2_range,
            _mids,
            _new_board
        ]

    def next(self, pos: int, who: int):
        ret = (pos + 1) % self.length

        if who == 1:
            return ret if ret != 0 else 1 # to make sure not in other persons thing
        
        elif who == 0:
            return ret if ret != self.mid else self.mid+1 # to make sure not in other persons thing
    
    def check_done(self, inputs: List[int]):
        return set(inputs[1:self.mid] + inputs[self.mid + 1:]) == set([0])

    def simulate(self, pos: int, inputs: List[int], player: int):
        # whos turn it is
        next_player = 1 - player # negates the player

        if inputs[pos] == 0:
            return [-1, inputs]

        # carry the thing
        carry = inputs[pos]
        inputs[pos] = 0

        while True:
            while carry != 0:
                pos = self.next(pos, player)

                # deposit an item
                carry -= 1
                inputs[pos] += 1

            # if doposited on empty or on the opponents field
            # if opponent, then check for field 0, else home field
            if pos == self.mids[player]:
                next_player = player
                break

            elif inputs[pos] != 1:
                carry = inputs[pos]
                inputs[pos] = 0

            else:
                break

        return (next_player, inputs)

    # minimax
    def tree_search(self, inputs: List[int], maximizing_player: int, depth: int):

        # terminal case
        if depth == 0 or maximizing_player == -1:
            return inputs[self.mid] - inputs[0]
        
        if maximizing_player == 1:
            possibilies = [self.simulate(pos=pos, inputs=inputs.copy(), player=maximizing_player) for pos in self.p1_range]
            return max([self.tree_search(inputs=p[1], maximizing_player=p[0], depth=depth - 1) for p in possibilies])
        
        else:
            possibilies = [self.simulate(pos=pos, inputs=inputs.copy(), player=maximizing_player) for pos in self.p2_range]
            return min([self.tree_search(inputs=p[1], maximizing_player=p[0], depth=depth - 1) for p in possibilies])

    def solve(self, depth: int = 1):
        # simulate the first move
        first_moves = [self.simulate(pos=pos, inputs=self.inputs.copy(), player=1) for pos in self.p1_range]

        outcomes = [self.tree_search(inputs=move[1], maximizing_player=move[0], depth=depth - 1) for move in first_moves]
        best_outcome = max(outcomes)

        # get correctsponding move
        best_pos = outcomes.index(best_outcome) + 1 # +1 because 0-index
        return best_pos
