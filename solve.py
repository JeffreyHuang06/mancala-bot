import builtins
from typing import List
from debug import visualize

ListSizeError = Exception("List size must be even number")

class Answer:
    def __init__(self, bst_move: int):
        self.best_move = bst_move
    
    def with_full_sim(self, full_sim, moves: List[int]):
        def exec_full_sim():
            full_sim(moves)

        self.full_sim = exec_full_sim

        return self

class Solver:
    def __init__(self, inputs: List[int], debug=0):
        self.mid, self.length, self.p1_range, self.p2_range, self.mids, self.inputs = Solver.resize_board(inputs)

        # debug is the debug level, debug:0 is none, debug:1 is show initialization, debug:2 is everything
        self.debug = debug

        print("Solver initialized\n")

        if debug > 0:
            print()
            print(f"mid: {self.mid}")
            print(f"length: {self.length}")
            print(f"p1_range: {self.p1_range}")
            print(f"p2_range: {self.p2_range}")
            print(f"inputs: {self.inputs}")
            print()
    
    @staticmethod
    def resize_board(board: List[int]):
        """
        Resizes board
        :returns
        [
            _mid,
            _length,
            _p1_range,
            _p2_range,
            _mids,
            _new_board
        ]
        """
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
        """
        Calculates the next position, accounts for cycles, skips on opponents pools\n
        If who==1 then skips from 0 to 1\n
        If who==0 then skips from mid to mid+1  
        """
        ret = (pos + 1) % self.length

        if who == 1:
            return ret if ret != 0 else 1 # to make sure not in other persons thing
        
        elif who == 0:
            return ret if ret != self.mid else self.mid+1 # to make sure not in other persons thing
    
    def check_done(self, inputs: List[int]):
        return set(inputs[1:self.mid] + inputs[self.mid + 1:]) == set([0])

    def simulate(self, pos: int, inputs: List[int], player: int):
        """
        shape: [next_player, post-simulated board]
        types: list[int, list[int]]
        out_shape: [pos, inputs]
        """
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

        return [next_player, inputs]

    def full_sim(self, moves: List[int]):
        states = [self.inputs]

        newstate = self.inputs
        next_player = 1
        
        for move in moves:
            # print(move)
            next_player, newstate = self.simulate(move, newstate.copy(), next_player)
            # print(next_player)
            states.append(newstate.copy())
        
        for state in states:
            visualize(state)

    # minimax
    def tree_search(self, inputs: List[int], maximizing_player: int, depth: int, moves: List[int]):
        """
        input_shape: inputs, moves
        output_shape(score): [score, moves]
            case-maximizing_player==1: None, will get filtered out
        """
        if maximizing_player == -1:
            return None

        # terminal case
        if depth == 0:
            # print(inputs[self.mid] - inputs[0])
            return (
                inputs[self.mid] - inputs[0],
                moves
            )
        
        if maximizing_player == 1:
            possibilies = [self.simulate(pos=pos, inputs=inputs.copy(), player=maximizing_player) for pos in self.p1_range]

            searched = [self.tree_search(inputs=p[1], maximizing_player=p[0], depth=depth - 1, moves=moves + [ind+1]) for ind, p in enumerate(possibilies)]
            searched = list(filter(lambda x: x != None, searched))
            score = max(searched, key=lambda x: x[0])
        
        else:
            possibilies = [self.simulate(pos=pos, inputs=inputs.copy(), player=maximizing_player) for pos in self.p2_range]

            searched = [self.tree_search(inputs=p[1], maximizing_player=p[0], depth=depth - 1, moves=moves + [ind+1]) for ind, p in enumerate(possibilies)]
            searched = list(filter(lambda x: x != None, searched))
            score = min(searched, key=lambda x: x[0])
        
        if self.debug > 1:
            print("searched:", searched)
            print("depth", depth)
            print("mp:", maximizing_player)
            print("score", score, '\n')

        return score

    def solve(self, depth: int = 1):
        # set up the first moves
        first_move = []
        for pos in self.p1_range:
            first_move.append(
                (self.simulate(
                        pos,
                        self.inputs.copy(),
                        1
                    ), pos)
            )
        first_move = list(filter(lambda x: x[0][0] != -1, first_move))

        outcomes = [
            self.tree_search(
                inputs=move[1],
                maximizing_player=move[0],
                depth=depth-1,
                moves=[pos])
            for move, pos in first_move
        ]

        best_outcome = max(outcomes, key=lambda x: x[0])
        # get correctsponding move
        best_pos = best_outcome[1][0]

        if self.debug > 0:
            print(f"first_moves: {first_move}")
            print(f"outcomes: {outcomes}")
            print(f"best outcome: {best_outcome}")
            print()
    
        return Answer(best_pos).with_full_sim(self.full_sim, best_outcome[1]) 

