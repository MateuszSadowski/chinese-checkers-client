import socket
import json
import random
import string
import time
import datetime

import gameState
import gameController
import messageDispatcher
import messageHandler
import socketHandler
import helper
import constants as const

print('Welcome to ChineseCheckers!')
# print('What is the ID of the game you want to connect to?')
# gameId = helper.getIntegersFromConsole()
gameId = const.GAME_ID

# Initialize game
gameState = gameState.GameState()
gameController = gameController.GameController()
socketHandler = socketHandler.SocketHandler(const.IP, const.PORT)
messageHandler = messageHandler.MessageHandler(gameState, gameController, socketHandler)
messageDispatcher = messageDispatcher.MessageDispatcher(gameState, gameController, socketHandler)

# TODO: handle case when failed to connect
username = helper.randomString()
messageDispatcher.connect()
messageDispatcher.login(username, gameId)

messageHandler.receiveAndProcessMessages()

print('[INFO] Waiting for game to start...\n')
messageHandler.receiveAndProcessMessages()

# Strategy functions
def evaluate(state): # player 2 maximizes evaluation, player 1 minimizes evaluation
    currentPositions = state['pawns']
    players = state['players']
    centerline = int(7)

    for player in players:
        playerID = player['id']
        boundary = player['boundary']
        vertDist = 0
        horDist = 0
        for pawn in currentPositions[playerID]:
            if pawn not in player['goalFields']:
                vertDist += abs(boundary - const.VERT_POS[int(pawn)])
                horDist += abs(centerline - const.HOR_POS[int(pawn)])
        if playerID == gameController.getMyPlayerID(state):
            maxPlayerVertDist = vertDist
            maxPlayerHorDist = horDist
        else:
            minPlayerVertDist = vertDist
            minPlayerHorDist = horDist

    return (minPlayerVertDist - maxPlayerVertDist) + (minPlayerHorDist - maxPlayerHorDist)

def printAllPawns():
    state = gameState.getState()
    pawns = gameController.getAllPawns(state)
    for key, value in pawns.items():
        print('Player {0} has pawns in {1}'.format(key, value))

def printAllPossibleMoves():
    state = gameState.getState()
    myPlayerID = gameController.getMyPlayerID(state)
    possibleMoves = gameController.allMoves(state, myPlayerID)
    print('Current evaluation: {0}'.format(evaluate(state)))
    for key, value in possibleMoves.items():
        nextFields = []
        for newField in value:
            nextFields.append(evaluatePossibleMove((key, newField), myPlayerID))
        print('Pawn {0} can move to {1}'.format(key, nextFields))

def evaluatePossibleMove(move, playerId):
    state = gameState.getState()
    newState = gameController.makeMove(state, move[0], move[1], playerId)
    return move[1], evaluate(newState)

# Wait for turn or make move
while not gameState.isFinished():
    while not gameState.isNextTurn():
        messageHandler.receiveAndProcessMessages()

    if gameState.isMyTurn():
        print('It\'s my turn!\n')
        # printAllPawns()
        gameController.printBoard(gameState.getState())
        printAllPossibleMoves()
        # TODO: make it possible to quit game
        print('Which pawn would you like to move?')
        oldField = helper.getIntegersFromConsole()
        print('Where would you like to move?')
        newField = helper.getIntegersFromConsole()
        messageDispatcher.sendMove(oldField, newField)

    messageHandler.receiveAndProcessMessages()