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
print('What is the ID of the game you want to connect to?')
gameId = helper.getIntegersFromConsole()

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
def printAllPawns():
    state = gameState.getState()
    pawns = gameController.getAllPawns(state)
    for key, value in pawns.items():
        print('Player {0} has pawns in {1}'.format(key, value))

def printAllPossibleMoves():
    state = gameState.getState()
    myPlayerID = gameController.getMyPlayerID(state)
    possibleMoves = gameController.allMoves(state, myPlayerID)
    for key, value in possibleMoves.items():
        print('Pawn {0} can move to {1}'.format(key, value))

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