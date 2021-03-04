from typing import List

def visualize(board: List[int]):
    length = len(board)
    halflen = length // 2

    vis = [[0]] + [[0,0] for _ in range(halflen-1)] + [[0]]
    vis[0][0] = board[0]
    vis[-1][0] = board[halflen]
    
    for i in range(1,halflen):
        vis[i] = [board[i], board[length - i -1]]
    
    for i in vis:
        print(i)
    print()