import json

import gameState
import helper

ID = 'id'
USERNAME = 'username'
START = 'start'
FIELDS = 'fields'
PLAYERS = 'players'
PLAYER = 'player'
SESSION = 'session'
PLAYER_ID = 'playerID'
CAUSE = 'cause'
RESULT = 'result'
BOARD = 'board'
TOTAL_MOVES = 'totalMoves'
TYPE = 'type'

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
        msg_info = json.loads(msg)
        msg_type = msg_info['type']
        if msg_type == PLAYER:
            self.handlePlayer(msg_info)
        elif msg_type == 'init':
            self.handleInit(msg_info)
        elif msg_type == 'turn':
            self.handleTurn(msg_info)
        elif msg_type == 'error':
            self.handleError(msg_info)
        elif msg_type == 'result':
            self.handleResult(msg_info)
        elif msg_type == 'info':
            self.handleInfo(msg_info['info'])
        else:
            print('!!ERROR!! Invalid message type')
        
    def handlePlayer(self, msg_info):
        currentState = self.gameState.getState()
        currentState[PLAYER] = {
            ID: msg_info[ID],
            USERNAME: msg_info[USERNAME],
            TOTAL_MOVES: 0
        }
        self.gameState.setState(currentState)
        print('[INFO] Player logged in with ID: {0} and username: {1}\n'.format(currentState[PLAYER][ID], currentState[PLAYER][USERNAME]))

    def handleInit(self, msg_info):
        currentState = self.gameState.getState()
        session_info = msg_info[SESSION];
        currentState[BOARD] = session_info[FIELDS]
        currentState[PLAYERS] = session_info[PLAYERS]
        newState = self.gameController.initializeState(currentState)
        self.gameState.setState(newState)
        print('[INFO] Game starts!\n')

    def handleTurn(self, msg_info):
        currentState = self.gameState.getState()
        newState = self.gameController.nextTurn(currentState, msg_info['playerID'])
        self.gameState.setState(newState)
        print('((TURN)) Turn of player with id: {0}\n'.format(newState['next_turn']))

    def handleInfo(self, msg_info):
        currentState = self.gameState.getState()
        oldField = str(msg_info['oldFieldID'])
        newField = str(msg_info['newFieldID'])
        playerId = currentState['board'][oldField]['player']
        
        # TODO: might need to do state['last_turn'] = state['next_turn'] here
        newState = self.gameController.makeMove(currentState, oldField, newField, playerId)
        self.gameState.setState(newState)

    def handleError(self, msg_info):
        print(msg_info[CAUSE])

    def handleResult(self, msg_info):
        currentState = self.gameState.getState()
        print('==================================================')
        print('<<RESULT>>')
        print('Game ended with result: {0}'.format(msg_info[RESULT]))
        if msg_info[PLAYER_ID] != -1:
            print('for player {1}'.format(msg_info[PLAYER_ID]))
        print('after {0} moves'.format(currentState['player']['totalMoves']))
        print('==================================================')
        newState = self.gameController.finishGame(currentState)
