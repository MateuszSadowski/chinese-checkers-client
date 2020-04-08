import socket
import json
import random
import string
import time
import datetime
import copy

import gameState
import gameController
import messageDispatcher
import messageHandler
import socketHandler
import helper
import constants as const

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

def GameOver(state,playerID):
    currentField = state['board']
    players = state['players']
    for i in range(len(players)):
        if players[i]["id"] == playerID:
            count = int(0) 
            player_in_goalState = False
            for key in players[i]["goalFields"]:
                if currentField[key]["player"] != None:
                    count += 1
                
                if currentField[key]["player"] == playerID:
                    player_in_goalState = True
    
    if count == 10 and player_in_goalState == True:
        return True
    else:
        return False

bestMaxMove = []
bestMinMove = []

# currentField == board
# currentPositions == pawns
def MiniMax(state,depth,alpha,beta,maximizingPlayersTurn): # MiniMax algorithm
    maxPlayer = gameController.getMyPlayerID(state)
    minPlayer = gameController.getOpponentID(state)

    if depth == 0 or GameOver(state,maxPlayer) or GameOver(state,minPlayer):
        return evaluate(state)

    if maximizingPlayersTurn:
        # availableNeighbours,occupiedNeighbours = AnalyzeNeighbours(currentPositions,currentField,maxPlayer)
        # availableBridges = AllBridges(InitializeBridge(occupiedNeighbours))
        # possibleMoves = CombineMoves(availableNeighbours, availableBridges, maxPlayer)
        possibleMoves = gameController.allMoves(state, maxPlayer)
        MaxEvaluation = -const.M_CONST
        for pawn,move in ((p,i) for p in possibleMoves for i in possibleMoves[p]):
            newState = copy.deepcopy(state)
            # newField = copy.deepcopy(currentField)
            # newPositions = copy.deepcopy(currentPositions)
            # print(depth,': from ',pawn,' to ',move)
            # info = {'createdAt':None,'newFieldID':int(move),'oldFieldID':int(pawn)}
            newState = gameController.makeMove(newState, pawn, move, maxPlayer)
            # UpdateField(newField,newPositions,info)
            evaluation = MiniMax(newState,depth - 1,alpha,beta,False)
            if const.MAX_DEPTH == depth and evaluation >= MaxEvaluation:
                bestMaxMove.append((pawn,move,evaluation))
            MaxEvaluation = max(MaxEvaluation, evaluation)
            alpha = max(alpha,MaxEvaluation)
            if beta <= alpha:
                break
        return MaxEvaluation
    
    else:
        # availableNeighbours,occupiedNeighbours = AnalyzeNeighbours(currentPositions,currentField,minPlayer)
        # availableBridges = AllBridges(InitializeBridge(occupiedNeighbours))
        # possibleMoves = CombineMoves(availableNeighbours, availableBridges, minPlayer)
        possibleMoves = gameController.allMoves(state, minPlayer)
        MinEvaluation = const.M_CONST
        for pawn,move in ((p,i) for p in possibleMoves for i in possibleMoves[p]):
            newState = copy.deepcopy(state)
            # newField = copy.deepcopy(currentField)
            # newPositions = copy.deepcopy(currentPositions)
            # print(depth,': from ',pawn,' to ',move)
            # info = {'createdAt':None,'newFieldID':int(move),'oldFieldID':int(pawn)}
            newState = gameController.makeMove(newState, pawn, move, minPlayer)
            # UpdateField(newField,newPositions,info)
            evaluation = MiniMax(newState,depth - 1,alpha,beta,True)
            if const.MAX_DEPTH == depth and evaluation <= MinEvaluation:
                bestMinMove.append((pawn,move,evaluation))
            MinEvaluation = min(MinEvaluation, evaluation)
            beta = min(beta,MinEvaluation)
            if beta <= alpha:
                break
        return MinEvaluation

def getRandomBestMove(bestMaxMove, bestMinMove):
    state = gameState.getState()
    
    print('Calculating MinMax...')
    startTime = time.time()
    MiniMax(state, const.MAX_DEPTH, -const.M_CONST, const.M_CONST, True)
    endTime = time.time()
    print('Calculated in ' + str(endTime - startTime) + ' seconds')

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

def getBestMove(bestMaxMove, bestMinMove):
    state = gameState.getState()
    
    print('Calculating MinMax...')
    startTime = time.time()
    MiniMax(state, const.MAX_DEPTH, -const.M_CONST, const.M_CONST, True)
    endTime = time.time()
    print('Calculated in ' + str(endTime - startTime) + ' seconds')

    if len(bestMaxMove) == 0:
        print('!!ERROR!! No possible moves for player: ' + str(gameController.getMyPlayerID(state)))
    moves = helper.maxes(bestMaxMove, key=lambda x: x[2]) # find all moves that has the same maximum evaluation value
    move = random.choice(moves[1]) # moves[0] - max evaluation value, moves[1] - list of moves with the maximum evaluation value
    oldField = move[0]
    newField = move[1]

    return oldField, newField

# Wait for turn or make move
while not gameState.isFinished():
    while not gameState.isNextTurn():
        messageHandler.receiveAndProcessMessages()

    if gameState.isMyTurn():
        print('It\'s my turn!\n')
        printAllPawns()
        oldField, newField = getBestMove(bestMaxMove, bestMinMove)
        bestMaxMove = []
        bestMinMove = []
        messageDispatcher.sendMove(oldField, newField)

    messageHandler.receiveAndProcessMessages()