import copy

class GameState:
    def __init__(self):  
        self.state = {
            'player': {}, # this player
            'players': [], # info about all players
            'board': {}, # current state of the game
            'pawns': {}, # current pawns' locations for each player
            'totalMoves': {}, # total number of moves for each player
            'nextTurn': -1, # player id
            'lastTurn': -1, # player id 
            'gameFinished': False,
            'gameWon': False
        }

    def getState(self):
        return copy.deepcopy(self.state)

    def setState(self, state):
        self.state = state

    def isNextTurn(self):
        return self.state['nextTurn'] != self.state['lastTurn']

    def isFinished(self):
        return self.state['gameFinished']

    def isMyTurn(self):
        return self.state['nextTurn'] == self.state['player']['id']

    def isWon(self):
        return self.state['gameWon']
