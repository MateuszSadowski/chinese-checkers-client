import socket
import json
import random
import string
import time
import datetime

import game
import helper

PORT = 8080
IP = 'localhost'

print('Welcome to ChineseCheckers!')
print('What is the ID of the game you want to connect to?')
game_id = helper.getIntegersFromConsole()

# Initialize game
game = game.Game()
# TODO: handle case when failed to connect
game.connect(IP, PORT)
game.loginAndWaitToStart(helper.randomString(), game_id)
game.initializeState()

# Strategy functions
def printAllPawns():
    pawns = game.getAllPawns()
    for key, value in pawns.items():
        print('Player {0} has pawns in {1}'.format(key, value))

def printAllPossibleMoves():
    possibleMoves = game.allMoves(game.getMyPlayerID())
    for key, value in possibleMoves.items():
        print('Pawn {0} can move to {1}'.format(key, value))

# Wait for turn or make move
while not game.isFinished():
    while not game.isNextTurn():
        game.receiveAndProcessMessages()

    if game.isMyTurn():
        print('It\'s my turn!\n')
        printAllPawns()
        printAllPossibleMoves()
        print('Which pawn would you like to move?')
        old_field = helper.getIntegersFromConsole()
        print('Where would you like to move?')
        new_field = helper.getIntegersFromConsole()
        game.createAndMakeMove(old_field, new_field)

    game.receiveAndProcessMessages()