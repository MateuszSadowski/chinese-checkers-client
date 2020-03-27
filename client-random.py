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
GAME_ID = 1

# Initialize game
game = game.Game()
# TODO: handle case when failed to connect
game.connect(IP, PORT)
game.loginAndWaitToStart(helper.randomString(), GAME_ID)
game.initializeState()

# Strategy functions
def getRandomPawn():
    pawns = game.getMyPawns()
    return random.choice(pawns)

def getRandomMove():
    myPlayerID = game.getMyPlayerID()
    possibleMoves = game.allMoves(myPlayerID)

    pawns = list(filter(lambda pawn: len(possibleMoves[pawn]) > 0, possibleMoves.keys())) # Get only pawns that have at least 1 possible move
    if len(pawns) == 0:
        print('!!ERROR!! No possible moves for player: ' + game.getMyPlayerID())
    pawn = random.choice(pawns)
    move = random.choice(possibleMoves[pawn])

    return pawn, move


# Wait for turn or make move
while not game.isFinished():
    while not game.isNextTurn():
        game.receiveAndProcessMessages()

    if game.isMyTurn():
        print('It\'s my turn!\n')
        pawn, next_move = getRandomMove()
        game.createAndMakeMove(pawn, next_move)

    game.receiveAndProcessMessages()