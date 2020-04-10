import socket
import json
import random
import string
import time
import datetime
import copy
import numpy as np

import gameState
import gameController
import messageDispatcher
import messageHandler
import socketHandler
import helper
import constants as const

print('\nWelcome to Chinese Checkers!\n')
print('Please, specify MinMax search depth (1 is random greedy):')
MAX_DEPTH = helper.getIntegersFromConsole()
print('')

# Initialize game
gameState = gameState.GameState()
gameController = gameController.GameController()
socketHandler = socketHandler.SocketHandler(const.IP, const.PORT)
messageHandler = messageHandler.MessageHandler(gameState, gameController, socketHandler)
messageDispatcher = messageDispatcher.MessageDispatcher(gameState, gameController, socketHandler)

# TODO: handle case when failed to connect
username = helper.randomString()
messageDispatcher.connect()
messageDispatcher.login(username, const.GAME_ID)

messageHandler.receiveAndProcessMessages()

print('[INFO] Waiting for game to start...\n')
messageHandler.receiveAndProcessMessages()

# Strategy functions
bestMaxMove = []
calculationTimes = []
nodesEvaluated = 0
allNodesEvaluated = []

def evaluate(state): # player 2 maximizes evaluation, player 1 minimizes evaluation
    currentPositions = state['pawns']
    players = state['players']
    centerline = int(7)

    for player in players:
        playerID = player['id']
        boundary = player['boundary']
        vertDist = 0
        horDist = 0
        endGame = 0
        for pawn in currentPositions[playerID]:
            if pawn not in player['goalFields']:
                vertDist += abs(boundary - const.VERT_POS[int(pawn)])
                horDist += abs(centerline - const.HOR_POS[int(pawn)])
        if playerID == gameController.getMyPlayerID(state):
            maxPlayerVertDist = vertDist
            maxPlayerHorDist = horDist
            if gameOver(state, playerID):
                endGame = 50
        else:
            minPlayerVertDist = vertDist
            minPlayerHorDist = horDist
            if gameOver(state, playerID):
                endGame = -50

    return 0.5 * (minPlayerVertDist - maxPlayerVertDist) + 0.5 * (minPlayerHorDist - maxPlayerHorDist) + endGame

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

def updateEvaluation(maximizingPlayersTurn, bestEval, currEval, alpha, beta):
    if maximizingPlayersTurn:
        bestEval = max(bestEval, currEval)
        alpha = max(alpha, bestEval)
    else:
        bestEval = min(bestEval, currEval)
        beta = min(beta, bestEval)

    return bestEval, alpha, beta

# currentField <==> board
# currentPositions <==> pawns
def minMax(state,depth,alpha,beta,maximizingPlayersTurn): # MinMax algorithm
    global nodesEvaluated
    maxPlayer = gameController.getMyPlayerID(state)
    minPlayer = gameController.getOpponentID(state)

    # TODO: most often the game is over, bc in the previous move the opponent won the game
    # can it be that we won the game bc of the previous move of the opponent?
    if depth == 0 or gameOver(state,maxPlayer) or gameOver(state,minPlayer):
        return evaluate(state)

    if maximizingPlayersTurn:
        playerId = maxPlayer
        bestEval = -const.M_CONST
    else:
        playerId = minPlayer
        bestEval = const.M_CONST

    possibleMoves = gameController.allMoves(state, playerId)

    # Evaluate first level
    # TODO: refactor
    if depth == MAX_DEPTH and maximizingPlayersTurn:
        sortedMoves = []
        for pawn,move in ((p,i) for p in possibleMoves for i in possibleMoves[p]):
            newState = copy.deepcopy(state)
            newState = gameController.makeMove(newState, pawn, move, playerId)
            nodesEvaluated += 1
            sortedMoves.append((evaluate(newState), pawn, move))
        sortedMoves.sort(reverse = True)
        possibleMoves = list(map(lambda x : (x[1], x[2]), sortedMoves))

        for possibleMove in possibleMoves:
            pawn = possibleMove[0]
            move = possibleMove[1]
            newState = copy.deepcopy(state)
            newState = gameController.makeMove(newState, pawn, move, playerId)
            nodesEvaluated += 1
            evaluation = minMax(newState, depth - 1, alpha, beta, not maximizingPlayersTurn)

            if maximizingPlayersTurn:
                if MAX_DEPTH == depth and evaluation >= bestEval:
                    bestMaxMove.append((pawn, move, evaluation))

            bestEval, alpha, beta = updateEvaluation(maximizingPlayersTurn, bestEval, evaluation, alpha, beta)

            if beta < alpha:
                break
    else:
        for pawn,move in ((p,i) for p in possibleMoves for i in possibleMoves[p]):
            newState = copy.deepcopy(state)
            newState = gameController.makeMove(newState, pawn, move, playerId)
            nodesEvaluated += 1
            evaluation = minMax(newState, depth - 1, alpha, beta, not maximizingPlayersTurn)

            if maximizingPlayersTurn:
                if MAX_DEPTH == depth and evaluation >= bestEval:
                    bestMaxMove.append((pawn, move, evaluation))

            bestEval, alpha, beta = updateEvaluation(maximizingPlayersTurn, bestEval, evaluation, alpha, beta)

            if beta < alpha:
                break

    return bestEval

def getRandomBestMove(bestMaxMove):
    state = gameState.getState()
    
    print('Calculating MinMax...')
    startTime = time.time()
    minMax(state, MAX_DEPTH, -const.M_CONST, const.M_CONST, True)
    calculationTime = time.time() - startTime
    print('Calculated in: ' + str(round(calculationTime, 2)) + ' seconds')
    calculationTimes.append(calculationTime)
    print('Average calculation time so far:' + str(round(mean(calculationTimes), 2)))

    if len(bestMaxMove) == 0:
        print('!!ERROR!! No possible moves for player: ' + str(gameController.getMyPlayerID(state)))
    move = random.choice(bestMaxMove)
    oldField = move[0]
    newField = move[1]

    return oldField, newField

def printAllPawns():
    state = gameState.getState()
    pawns = gameController.getAllPawns(state)
    for key, value in pawns.items():
        print('Player {0} has pawns in {1}'.format(key, value))

def getBestMove(bestMaxMove):
    state = gameState.getState()
    
    print('Calculating MinMax...\n')
    startTime = time.time()
    minMax(state, MAX_DEPTH, -const.M_CONST, const.M_CONST, True)
    calculationTime = time.time() - startTime
    print('Calculated in: ' + str(round(calculationTime, 2)) + ' seconds')
    calculationTimes.append(calculationTime)
    print('Average calculation time so far: ' + str(round(np.mean(calculationTimes), 2)) + ' seconds')
    print('Max calculation time so far: ' + str(round(np.max(calculationTimes), 2)) + ' seconds')
    print('Min calculation time so far: ' + str(round(np.min(calculationTimes), 2)) + ' seconds\n')

    print('No. of evaluated moves: {0}'.format(nodesEvaluated))
    allNodesEvaluated.append(nodesEvaluated)
    # averageNodesEvaluated = sumNodesEvaluated / mainLoopIterations
    print('Average no. of evaluated moves so far: {0}'.format(round(np.mean(allNodesEvaluated), 0)))
    print('Max no. of evaluated moves so far: {0}'.format(np.max(allNodesEvaluated)))
    print('Min no. of evaluated moves so far: {0}'.format(np.min(allNodesEvaluated)))

    if len(bestMaxMove) == 0:
        print('!!ERROR!! No possible moves for player: ' + str(gameController.getMyPlayerID(state)))
    moves = helper.maxes(bestMaxMove, key=lambda x: x[2]) # find all moves that has the same maximum evaluation value
    move = random.choice(moves[1]) # moves[0] - max evaluation value, moves[1] - list of moves with the maximum evaluation value
    oldField = move[0]
    newField = move[1]

    return oldField, newField

def printPossibleMoves(bestMaxMove):
    print('')
    print('Current evaluation: {0}'.format(evaluate(gameState.getState())))
    print('Possible moves:')
    for move in bestMaxMove:
        print('Pawn {0} to {1} evaluated as: {2}'.format(move[0], move[1], round(move[2], 2)))
    print('')

# Wait for turn or make move
while not gameState.isFinished():
    while not gameState.isNextTurn():
        messageHandler.receiveAndProcessMessages()

    if gameState.isMyTurn():
        print('It\'s my turn!\n')
        # printAllPawns()
        gameController.printBoard(gameState.getState())
        oldField, newField = getBestMove(bestMaxMove)
        printPossibleMoves(bestMaxMove)
        bestMaxMove = [] # reset
        nodesEvaluated = 0
        messageDispatcher.sendMove(oldField, newField)

    messageHandler.receiveAndProcessMessages()