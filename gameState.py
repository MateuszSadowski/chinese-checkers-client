import copy

class GameState:
    def __init__(self):  
        self.state = {
            'player': {}, # this player
            'players': [], # info about all players
            'board': {}, # current state of the game
            'pawns': {}, # current pawns' locations for each player
            'next_turn': -1, # player id
            'last_turn': -1, # player id 
            'game_finished': False
        }

    def getState(self):
        return copy.deepcopy(self.state)

    def setState(self, state):
        self.state = state
