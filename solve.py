import builtins
from typing import List
from debug import visualize, disp_list, depr_check
from threading import Thread
from multiprocessing import Process, Queue
from queue import Queue as default_Queue
from exceptions import ListSizeError

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

    def check_complete(self, inputs: List[int]):
        return set(inputs[1:self.mid] + inputs[self.mid + 1:-1]) == set([0])

    def check_done(self, inputs: List[int]):
        # check if theres all 0 on a thing
        return set(inputs[1:self.mid]) == set([0]) or set(inputs[self.mid + 1:-1]) == set([0])

    def terminal_allocate(self, inputs: List[int], player: int):
        if player == 1:
            # get the score
            score = sum(inputs[1:self.mid])

            # add to player
            inputs[self.mid] += score

            # remove all from the field
            for i in range(1, self.mid): inputs[i] = 0

            return inputs
        
        else:
            # get the score
            score = sum(inputs[self.mid + 1:-1])

            # add to player
            inputs[0] += score

            # remove all from the field
            for i in range(self.mid+1, self.length-1): inputs[i] = 0

            return inputs

    def simulate(self, pos: int, inputs: List[int], player: int):
        """
        shape: [next_player, post-simulated board]
        types: list[int, list[int]]
        out_shape: [pos, inputs]
        """
        # whos turn it is
        next_player = 1 - player # negates the player

        # check if this is invalid
        if inputs[pos] == 0:
            # terminal case
            if self.check_done(inputs): return [next_player, self.terminal_allocate(inputs.copy(), player)]

            else: return [-1, inputs]

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
    # TODO: alpha beta pruning
    def tree_search(self, inputs: List[int], maximizing_player: int, depth: int, moves: List[int]):
        """
        input_shape: inputs, moves
        output_shape(score): [score, moves]
            case-maximizing_player==1: None, will get filtered out
        """
        if maximizing_player == -1:
            return None

        # terminal case
        if depth == 0 or self.check_complete(inputs):
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

    # interface funcs
    def get_first_moves(self):
        first_move = []
        for pos in self.p1_range:
            first_move.append(
                (self.simulate(pos, self.inputs.copy(), 1), pos)
            )
        first_move = list(filter(lambda x: x[0][0] != -1, first_move))

        self.first_move = first_move

    def get_outcomes(self):
        self.outcomes = [
            self.tree_search(
                inputs=move[1],
                maximizing_player=move[0],
                depth=self.depth-1,
                moves=[pos])
            for move, pos in self.first_move
        ]

    def solve(self, depth: int = 1):
        self.depth = depth

        # set up the first moves
        self.get_first_moves()

        self.get_outcomes()

        best_outcome = max(self.outcomes, key=lambda x: x[0])
        # get correctsponding move
        best_pos = best_outcome[1][0]

        if self.debug > 0:
            print("first_moves: "); disp_list(self.first_move)
            print("outcomes: "); disp_list(self.outcomes)
            print(f"best outcome: {best_outcome}")
            print()

        return Answer(best_pos).with_full_sim(self.full_sim, best_outcome[1]) 


class Solver_MT (Solver):
    """
    (Deprecated) Multiprocessing, does not support alpha-beta pruning
    """

    def __init__(self, inputs: List[int], debug=0):
        # deprecation
        depr_check()

        super().__init__(inputs, debug)

    def simulate(self, pos: int, inputs: List[int], player: int, q=None):
        """
        shape: [next_player, post-simulated board]
        types: list[int, list[int]]
        out_shape: [pos, inputs]
        """
        # stores original pos
        original_pos = pos
        # whos turn it is
        next_player = 1 - player # negates the player

        if inputs[pos] == 0:
            if q != None: q.put([-1, inputs])
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
        
        if q != None:
            q.put([next_player, inputs, original_pos])

        return [next_player, inputs]

    # minimax
    def tree_search(self, inputs: List[int], maximizing_player: int, depth: int, moves: List[int], q=None):
        """
        input_shape: inputs, moves
        output_shape(score): [score, moves]
            case-maximizing_player==1: None, will get filtered out
        """
        if maximizing_player == -1:
            if q != None:
                q.put(None)

            return None

        # terminal case
        if depth == 0:
            # print(inputs[self.mid] - inputs[0])
            if q != None:
                q.put((inputs[self.mid] - inputs[0], moves))

            return (
                inputs[self.mid] - inputs[0],
                moves
            )
        
        # thread this
        possibilities = [self.simulate(pos=pos, inputs=inputs.copy(), player=maximizing_player) for pos in [self.p2_range, self.p1_range][maximizing_player]]

        if maximizing_player == 1:
            searched = [self.tree_search(inputs=p[1], maximizing_player=p[0], depth=depth - 1, moves=moves + [ind+1]) for ind, p in enumerate(possibilities)]
            searched = list(filter(lambda x: x != None, searched))
            score = max(searched, key=lambda x: x[0])
        
        else:
            searched = [self.tree_search(inputs=p[1], maximizing_player=p[0], depth=depth - 1, moves=moves + [ind+1]) for ind, p in enumerate(possibilities)]
            searched = list(filter(lambda x: x != None, searched))

            score = min(searched, key=lambda x: x[0])
        
        if self.debug > 1:
            print("searched:", searched)
            print("depth", depth)
            print("mp:", maximizing_player)
            print("score", score, '\n')

        # THREAD
        if q != None:
            q.put(score)

        return score

    # interface funcs
    def get_first_moves(self):
        first_move = []

        # do threading
        threads = []
        q = default_Queue()
        for pos in self.p1_range:
            t = Thread(target=self.simulate, args=(
                pos, self.inputs.copy(), 1, q))
            threads.append(t)
            t.start()
        for thread in threads:
            thread.join()
        for thread in threads:
            next_player, inputs, pos = q.get()
            first_move.append(([next_player, inputs], pos))

        first_move = list(filter(lambda x: x[0][0] != -1, first_move))

        self.first_move = first_move

    def get_outcomes(self):
        outcomes = []

        procs = []
        q = Queue()
        for move, pos in self.first_move:
            proc = Process(target=self.tree_search, args=(
                move[1], move[0], self.depth-1, [pos], q))
            procs.append(proc)
            proc.start()

        threads_completed = 0
        for proc in procs:
            proc.join()

            if self.debug > 0:
                threads_completed += 1
                print(f"Thread {threads_completed} Joined")

        if self.debug > 0:
            print()

        for proc in procs:
            outcomes.append(q.get())
        
        self.outcomes = outcomes
