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
        if messages != -1:
            for msg in messages:
                self.handleMessage(msg)
        else:
            currentState = self.gameState.getState()
            newState = self.gameController.finishGame(currentState)
            self.gameState.setState(newState)

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
            'username': msgInfo['username']
        }
        self.gameState.setState(currentState)
        print('[INFO] Player logged in with ID: {0} and username: {1}\n'.format(currentState['player']['id'], currentState['player']['username']))

    def handleInit(self, msgInfo):
        currentState = self.gameState.getState()
        sessionInfo = msgInfo['session'];
        currentState['board'] = sessionInfo['fields']
        for player in sessionInfo['players']:
            playerId = player['id']
            currentState['totalMoves'][playerId] = 0
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
        newState = self.gameController.makeMove(newState, oldField, newField, playerId)
        newState = self.gameController.incrementTotalMoves(newState, playerId)
        totalPlayerMoves = newState['totalMoves'][playerId]
        print('==MOVE-{3}==> Player {0} made a move from {1} to {2}\n'.format(playerId, oldField, newField, totalPlayerMoves))
        self.gameState.setState(newState)

    def handleError(self, msgInfo):
        print(msgInfo['cause'])

    def handleResult(self, msgInfo):
        currentState = self.gameState.getState()
        playerId = msgInfo['playerID']
        myPlayerId = self.gameController.getMyPlayerID(currentState)
        print('==================================================')
        if playerId != -1:
            if playerId == myPlayerId:
                print('<<RESULT>> {0} after {1} moves'.format(msgInfo['result'], currentState['totalMoves'][msgInfo['playerID']]))
                currentState = self.gameController.setWonGame(currentState)
                newState = self.gameController.finishGame(currentState)
                self.gameState.setState(newState)
            else:
                print('<<RESULT>> LOST after {0} moves'.format(currentState['totalMoves'][myPlayerId]))
        else:
            print('<<RESULT>> {0}'.format(msgInfo['result']))
        print('==================================================\n')
