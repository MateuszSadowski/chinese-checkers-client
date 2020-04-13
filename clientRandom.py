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

def main(argv):
    global gameId
    try:
        opts, args = getopt.getopt(argv,"hg:")
    except getopt.GetoptError:
        print('clientRandom.py -g <game-id(int)>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('clientRandom.py -g <game-id(int)>')
            sys.exit()
        elif opt in ("-g"):
            gameId = int(arg)
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
def getRandomPawn():
    state = gameState.getState()
    pawns = game.getMyPawns(state)
    return random.choice(pawns)

def getRandomMove():
    state = gameState.getState()
    myPlayerID = gameController.getMyPlayerID(state)
    possibleMoves = gameController.allMoves(state, myPlayerID)

    pawns = list(filter(lambda pawn: len(possibleMoves[pawn]) > 0, possibleMoves.keys())) # Get only pawns that have at least 1 possible move
    if len(pawns) == 0:
        print('!!ERROR!! No possible moves for player: ' + gameController.getMyPlayerID(state))
    oldField = random.choice(pawns)
    newField = random.choice(possibleMoves[oldField])

    return oldField, newField

# Wait for turn or make move
while not gameState.isFinished():
    while not gameState.isNextTurn() and not gameState.isFinished():
        messageHandler.receiveAndProcessMessages()

    if not gameState.isFinished():
        if gameState.isMyTurn():
            print('It\'s my turn!\n')
            oldField, newField = getRandomMove()
            messageDispatcher.sendMove(oldField, newField)

        messageHandler.receiveAndProcessMessages()