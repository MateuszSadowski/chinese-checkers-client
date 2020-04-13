import socket
import json
import random
import string
import time
import datetime
import sys
import getopt

import gameState
import gameController
import messageDispatcher
import messageHandler
import socketHandler
import helper
import constants as const

print('\nWelcome to Chinese Checkers!\n')

gameId = 0
showPossibleMoves = False
showMoveEvaluation = False

def main(argv):
    global gameId
    global showPossibleMoves
    global showMoveEvaluation
    try:
        opts, args = getopt.getopt(argv,"hg:", ['show-moves','show-eval'])
    except getopt.GetoptError:
        print('clientConsole.py -g <game-id(int)>')
        print('--show-moves - print all legal moves for player')
        print('--show-eval - calculate and print evaluation for all legal moves (requires --show-moves to have an effect)')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('clientConsole.py -g <game-id(int)>')
            print('--show-moves - print all legal moves for player')
            print('--show-eval - calculate and print evaluation for all legal moves (requires --show-moves to have an effect)')
            sys.exit()
        elif opt in ("-g"):
            gameId = int(arg)
        elif opt in ('--show-moves'):
            showPossibleMoves = True
        elif opt in ('--show-eval'):
            showMoveEvaluation = True
    print('Game ID is: ' + str(gameId))
    print('This parameter can be passed as command line argument\n')

if __name__ == "__main__":
   main(sys.argv[1:])

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
        maxPlayer = gameController.getMyPlayerID(state)
        vertDist = 0
        horDist = 0
        for pawn in currentPositions[playerID]:
            if pawn not in player['goalFields']:
                vertDist += abs(boundary - const.VERT_POS[int(pawn)])
                horDist += abs(centerline - const.HOR_POS[int(pawn)])
        if playerID == maxPlayer:
            maxPlayerVertDist = vertDist
            maxPlayerHorDist = horDist
        else:
            minPlayerVertDist = vertDist
            minPlayerHorDist = horDist

    endGameMaxPlayer = gameOver(state, maxPlayer)
    endGameMinPlayer = gameOver(state, gameController.getOpponentID(state))
    m = 0.5
    E = 50
    return m * (minPlayerVertDist - maxPlayerVertDist) + (1 - m) * (minPlayerHorDist - maxPlayerHorDist) + E * (endGameMaxPlayer - endGameMinPlayer)

def gameOver(state,playerID):
    currentField = state['board']
    players = state['players']
    for player in players:
        if player["id"] == playerID:
            count = int(0) 
            playerInGoalState = False
            for key in player["goalFields"]:
                if currentField[key]["player"] != None:
                    count += 1
                
                if currentField[key]["player"] == playerID:
                    playerInGoalState = True
    
    return count == 10 and playerInGoalState

def printAllPawns():
    state = gameState.getState()
    pawns = gameController.getAllPawns(state)
    for key, value in pawns.items():
        print('Player {0} has pawns in {1}'.format(key, value))

def getPossibleMoves():
    state = gameState.getState()
    myPlayerID = gameController.getMyPlayerID(state)
    possibleMoves = gameController.allMoves(state, myPlayerID)

    return possibleMoves

def printAllPossibleMoves(possibleMoves):
    state = gameState.getState()
    myPlayerID = gameController.getMyPlayerID(state)
    if showMoveEvaluation:
        print('Current evaluation: {0}'.format(evaluate(state)))
    for key, value in possibleMoves.items():
        nextFields = []
        for newField in value:
            if showMoveEvaluation:
                nextFields.append(evaluatePossibleMove((key, newField), myPlayerID))
            else:
                nextFields.append(newField)
        print('Pawn {0} can move to {1}'.format(key, nextFields))
    print('')

def evaluatePossibleMove(move, playerId):
    state = gameState.getState()
    newState = gameController.makeMove(state, move[0], move[1], playerId)
    return move[1], evaluate(newState)

def validateMove(oldField, newField, possibleMoves):
    try:
        possibleNewFields = possibleMoves[str(oldField)]
    except:
        # key error
        print('Invalid move. Cannot move pawn from field: {0}'.format(oldField))
        print('Choose a valid move and try again.\n')
        return False

    if not (str(newField) in possibleNewFields):
        print('Invalid move. Cannot move pawn: {0} to field: {1}'.format(oldField, newField))
        print('Choose a valid move and try again.\n')
        return False

    return True


def getMoveFromConsole():
    print('Which pawn would you like to move?')
    oldField = helper.getIntegersFromConsole()
    print('Where would you like to move?')
    newField = helper.getIntegersFromConsole()
    print('')

    return oldField, newField

# Wait for turn or make move
while not gameState.isFinished():
    while not gameState.isNextTurn() and not gameState.isFinished():
        messageHandler.receiveAndProcessMessages()

    if not gameState.isFinished():
        if gameState.isMyTurn():
            print('It\'s my turn!\n')
            gameController.printBoard(gameState.getState())
            possibleMoves = getPossibleMoves()
            if showPossibleMoves:
                printAllPossibleMoves(possibleMoves)
            oldField, newField = getMoveFromConsole()
            while not validateMove(oldField, newField, possibleMoves):
                oldField, newField = getMoveFromConsole()
            messageDispatcher.sendMove(oldField, newField)

        messageHandler.receiveAndProcessMessages()