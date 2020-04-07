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

PORT = 8080
IP = 'localhost'

print('Welcome to ChineseCheckers!')
# print('What is the ID of the game you want to connect to?')
# gameId = helper.getIntegersFromConsole()
gameId = 47

# Initialize game
gameState = gameState.GameState()
gameController = gameController.GameController()
socketHandler = socketHandler.SocketHandler(IP, PORT)
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
verticalPosition = [5,5,5,5,5,
                    6,6,6,6,6,6,
                    7,7,7,7,7,7,7,
                    8,8,8,8,8,8,8,8,
                    9,9,9,9,9,9,9,9,9,
                    10,10,10,10,10,10,10,10,
                    11,11,11,11,11,11,11,
                    12,12,12,12,12,12,
                    13,13,13,13,13,
                    4,4,4,4,
                    3,3,3,
                    2,2,
                    1,
                    5,6,7,8,
                    5,6,7,
                    5,6,
                    5,
                    10,11,12,13,
                    11,12,13,
                    12,13,
                    13,
                    14,14,14,14,
                    15,15,15,
                    16,16,
                    17,
                    13,12,11,10,
                    13,12,11,
                    13,12,
                    13,
                    8,7,6,5,
                    7,6,5,
                    6,5,
                    5]

horizontalPosition = [9,8,7,6,5,
                      9.5,8.5,7.5,6.5,5.5,4.5,
                      10,9,8,7,6,5,4,
                      10.5,9.5,8.5,7.5,6.5,5.5,4.5,3.5,
                      11,10,9,8,7,6,5,4,3,
                      10.5,9.5,8.5,7.5,6.5,5.5,4.5,3.5,
                      10,9,8,7,6,5,4,
                      9.5,8.5,7.5,6.5,5.5,4.5,
                      9,8,7,6,5,
                      8.5,7.5,6.5,5.5,
                      8,7,6,
                      7.5,6.5,
                      7,                    
                      4,3.5,3,2.5,
                      3,2.5,2,
                      2,1.5,
                      1,
                      2.5,3,3.5,4,
                      2,2.5,3,
                      1.5,2,
                      1,
                      5.5,6.5,7.5,8.5,
                      6,7,8,
                      6.5,7.5,
                      7,
                      10,10.5,11,11.5,
                      11,11.5,12,
                      12,12.5,
                      13,
                      11.5,11,10.5,10,
                      12,11.5,11,
                      12.5,12,
                      13]

def printAllPawns():
    state = gameState.getState()
    pawns = gameController.getAllPawns(state)
    for key, value in pawns.items():
        print('Player {0} has pawns in {1}'.format(key, value))

def printAllPossibleMoves():
    state = gameState.getState()
    myPlayerID = gameController.getMyPlayerID(state)
    possibleMoves = gameController.allMoves(state, myPlayerID)
    print('Current evaluation: {0}'.format(evaluation(state)))
    for key, value in possibleMoves.items():
        nextFields = []
        for newField in value:
            nextFields.append(evaluatePossibleMove((key, newField), myPlayerID))
        print('Pawn {0} can move to {1}'.format(key, nextFields))

def evaluate(state): # player 2 maximizes evaluation, player 1 minimizes evaluation
    currentPositions = state['pawns']
    players = state['players']
    verticalDistance = []
    horizontalDistance = []
    centerline = int(7)

    # TODO: refactor this
    myPlayerId = gameController.getMyPlayerID(state)
    sortedPlayers = [None, None]
    for player in players:
        if player['id'] == myPlayerId:
            sortedPlayers[0] = player
        else:
            sortedPlayers[1] = player

    for i in range(len(sortedPlayers)):
        playerID = sortedPlayers[i]['id']
        boundary = sortedPlayers[i]['boundary']
        vertDist = 0
        horDist = 0
        for pawn in currentPositions[playerID]:
            if pawn not in sortedPlayers[i]['goalFields']:
                vertDist += abs(boundary - verticalPosition[int(pawn)])
                horDist += abs(centerline - horizontalPosition[int(pawn)])
        verticalDistance.append(vertDist)
        horizontalDistance.append(horDist)
    evaluation = (verticalDistance[1] - verticalDistance[0]) + (horizontalDistance[1] - horizontalDistance[0])
    return evaluation

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
        printAllPawns()
        printAllPossibleMoves()
        # TODO: make it possible to quit game
        print('Which pawn would you like to move?')
        oldField = helper.getIntegersFromConsole()
        print('Where would you like to move?')
        newField = helper.getIntegersFromConsole()
        messageDispatcher.sendMove(oldField, newField)

    messageHandler.receiveAndProcessMessages()