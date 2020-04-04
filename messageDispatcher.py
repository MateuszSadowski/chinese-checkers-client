import json
import datetime

class MessageDispatcher:
    def __init__(self, gameState, gameController, socketHandler):
        self.gameState = gameState
        self.gameController = gameController
        self.socketHandler = socketHandler

    def connect(self):
        self.socketHandler.connect()

    def login(self, username, gameId):
        user = {
            'username': username,
            'gameID': gameId
        }

        loginMsg = json.dumps(user)
        self.socketHandler.send(loginMsg)

    def sendMove(self, oldField, newField):
        state = self.gameState.getState()
        newState = self.gameController.finishTurn(state)
        self.gameState.setState(newState)
        move = { 
            'createdAt': datetime.datetime.now().isoformat() + '+00:00',
            'oldFieldID': oldField,
            'newFieldID': newField
        }
        moveMsg = json.dumps(move)
        self.socketHandler.send(moveMsg)