import socket
import json
import random
import string
import time
import datetime
import copy
import numpy as np
import csv
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

maxDepth = 3
evalWeight = 0.5
gameId = 0

def main(argv):
    global maxDepth
    global evalWeight
    global gameId
    try:
        opts, args = getopt.getopt(argv,"hd:w:g:")
    except getopt.GetoptError:
        print('clientMinmax.py -d <max-search-depth(int)>=3 -w <evaluation-weight(float)>=0.5 -g <game-id(int)>=0')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('clientMinmax.py -d <max-search-depth(int)>=3 -w <evaluation-weight(float)>=0.5 -g <game-id(int)>=0')
            sys.exit()
        elif opt in ("-d"):
            maxDepth = int(arg)
        elif opt in ("-w"):
            evalWeight = float(arg)
        elif opt in ("-g"):
            gameId = int(arg)
    print('Max search depth is: ' + str(maxDepth))
    print('Evaluation weight is: ' + str(evalWeight))
    print('Game ID is: ' + str(gameId))
    print('These parameters can be passed as command line arguments\n')

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

if not gameState.isFinished():
    messageHandler.receiveAndProcessMessages()

if not gameState.isFinished():
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
    m = evalWeight
    E = 50 # TODO: move to constants.py
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
    if depth == maxDepth and maximizingPlayersTurn:
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
                if maxDepth == depth and evaluation >= bestEval:
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
                if maxDepth == depth and evaluation >= bestEval:
                    bestMaxMove.append((pawn, move, evaluation))

            bestEval, alpha, beta = updateEvaluation(maximizingPlayersTurn, bestEval, evaluation, alpha, beta)

            if beta < alpha:
                break

    return bestEval

def getRandomBestMove(bestMaxMove):
    state = gameState.getState()
    
    print('Calculating MinMax...')
    startTime = time.time()
    minMax(state, maxDepth, -const.M_CONST, const.M_CONST, True)
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
    minMax(state, maxDepth, -const.M_CONST, const.M_CONST, True)
    calculationTime = time.time() - startTime
    print('Calculated in: ' + str(round(calculationTime, 2)) + ' seconds')
    calculationTimes.append(calculationTime)
    print('Average calculation time so far: ' + str(round(np.mean(calculationTimes), 2)) + ' seconds')
    print('Max calculation time so far: ' + str(round(np.max(calculationTimes), 2)) + ' seconds')
    print('Min calculation time so far: ' + str(round(np.min(calculationTimes), 2)) + ' seconds')
    print('Total calculation time so far: ' + str(round(np.sum(calculationTimes), 2)) + ' seconds\n')

    print('No. of evaluated moves: {0}'.format(nodesEvaluated))
    allNodesEvaluated.append(nodesEvaluated)
    # averageNodesEvaluated = sumNodesEvaluated / mainLoopIterations
    print('Average no. of evaluated moves so far: {0}'.format(round(np.mean(allNodesEvaluated), 0)))
    print('Max no. of evaluated moves so far: {0}'.format(np.max(allNodesEvaluated)))
    print('Min no. of evaluated moves so far: {0}'.format(np.min(allNodesEvaluated)))
    print('Total no. of evaluated moves so far: {0}'.format(np.sum(allNodesEvaluated)))

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
    while not gameState.isNextTurn() and not gameState.isFinished():
        messageHandler.receiveAndProcessMessages()

    if not gameState.isFinished():
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

# Game finished, write stats to file
if len(calculationTimes) == len(allNodesEvaluated):
    statsFileName = 'stats/game-' + str(gameId) + "-" + str(datetime.datetime.now().isoformat()) + '-minmax-depth' + str(maxDepth) + '-weight' + str(evalWeight) + '-stats.csv'
    helper.createDirs(statsFileName)
    with open(statsFileName, 'w+', newline='') as file:
        writer = csv.writer(file, quoting = csv.QUOTE_NONNUMERIC)
        for i in range(len(calculationTimes)):
            writer.writerow([calculationTimes[i], allNodesEvaluated[i]])

        file.close()

    print('Game stats saved to: ')
    print(statsFileName)
else:
    print('Could not write game stats to file')