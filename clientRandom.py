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
GAME_ID = 14

# Initialize game
gameState = gameState.GameState()
gameController = gameController.GameController()
socketHandler = socketHandler.SocketHandler(IP, PORT)
messageHandler = messageHandler.MessageHandler(gameState, gameController, socketHandler)
messageDispatcher = messageDispatcher.MessageDispatcher(socketHandler)

# TODO: handle case when failed to connect
username = helper.randomString()
messageDispatcher.connect()
messageDispatcher.login(username, GAME_ID)

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
while not gameController.isFinished(gameState.getState()):
    while not gameController.isNextTurn(gameState.getState()):
        messageHandler.receiveAndProcessMessages()

    if gameController.isMyTurn(gameState.getState()):
        print('It\'s my turn!\n')
        oldField, newField = getRandomMove()
        messageDispatcher.sendMove(oldField, newField)

    messageHandler.receiveAndProcessMessages()