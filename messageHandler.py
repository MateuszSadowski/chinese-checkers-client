import json

import gameState
import helper

class MessageHandler:
    def __init__(self, gameState, gameController, socketHandler):
        self.gameState = gameState
        self.gameController = gameController
        self.socketHandler = socketHandler

    def receiveAndProcessMessages(self):
        messages = self.socketHandler.receiveAndSplitMessages()
        if(messages != -1):
            for msg in messages:
                self.handleMessage(msg)

    def handleMessage(self, msg):
        msgInfo = json.loads(msg)
        msgType = msgInfo['type']
        if msgType == 'player':
            self.handlePlayer(msgInfo)
        elif msgType == 'init':
            self.handleInit(msgInfo)
        elif msgType == 'turn':
            self.handleTurn(msgInfo)
        elif msgType == 'error':
            self.handleError(msgInfo)
        elif msgType == 'result':
            self.handleResult(msgInfo)
        elif msgType == 'info':
            self.handleInfo(msgInfo['info'])
        else:
            print('!!ERROR!! Invalid message type')
        
    def handlePlayer(self, msgInfo):
        currentState = self.gameState.getState()
        currentState['player'] = {
            'id': msgInfo['id'],
            'username': msgInfo['username'],
            'totalMoves': 0
        }
        self.gameState.setState(currentState)
        print('[INFO] Player logged in with ID: {0} and username: {1}\n'.format(currentState['player']['id'], currentState['player']['username']))

    def handleInit(self, msgInfo):
        currentState = self.gameState.getState()
        sessionInfo = msgInfo['session'];
        currentState['board'] = sessionInfo['fields']
        currentState['players'] = sessionInfo['players']
        newState = self.gameController.initializeState(currentState)
        self.gameState.setState(newState)
        print('[INFO] Game starts!\n')

    def handleTurn(self, msgInfo):
        currentState = self.gameState.getState()
        newState = self.gameController.nextTurn(currentState, msgInfo['playerID'])
        self.gameState.setState(newState)
        print('((TURN)) Turn of player with id: {0}\n'.format(newState['nextTurn']))

    def handleInfo(self, msgInfo):
        currentState = self.gameState.getState()
        oldField = str(msgInfo['oldFieldID'])
        newField = str(msgInfo['newFieldID'])
        playerId = currentState['board'][oldField]['player']
        
        newState = self.gameController.finishTurn(currentState)
        newState = self.gameController.makeMove(currentState, oldField, newField, playerId)
        self.gameState.setState(newState)

    def handleError(self, msgInfo):
        print(msgInfo['cause'])

    def handleResult(self, msgInfo):
        currentState = self.gameState.getState()
        print('==================================================')
        print('<<RESULT>>')
        print('Game ended with result: {0}'.format(msgInfo['result']))
        if msgInfo['playerID'] != -1:
            print('for player {1}'.format(msgInfo['playerID']))
        print('after {0} moves'.format(currentState['player']['totalMoves']))
        print('==================================================')
        newState = self.gameController.finishGame(currentState)
