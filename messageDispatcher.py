import json
import datetime

class MessageDispatcher:
    def __init__(self, gameState, gameController, socketHandler):
        self.gameState = gameState
        self.gameController = gameController
        self.socketHandler = socketHandler

    def connect(self):
        self.socketHandler.connect()

    def login(self, username, game_id):
        user = {
            'username': username,
            'gameID': game_id
        }

        login_msg = json.dumps(user)
        self.socketHandler.send(login_msg)

    def sendMove(self, oldField, newField):
        state = self.gameState.getState()
        newState = self.gameController.finishTurn(state)
        self.gameState.setState(newState)
        move = { 
            'createdAt': datetime.datetime.now().isoformat() + '+00:00',
            'oldFieldID': oldField,
            'newFieldID': newField
        }
        move_msg = json.dumps(move)
        self.socketHandler.send(move_msg)