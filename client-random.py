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
GAME_ID = 32

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
    availableNeighbours,occupiedNeighbours = game.analyzeNeighboursForAllPlayerPawns(myPlayerID)
    availableBridges = game.allBridges(game.initializeBridge(occupiedNeighbours))
    possibleMoves = game.allMoves(availableNeighbours, availableBridges, myPlayerID)

    neighbours = game.getFieldNeighbours(pawn)

    for key, field in neighbours.items():
        if game.getPawnInField(field) is None:
            return field

    return -1   # No available moves for this pawn


# Wait for turn or make move
while not game.isFinished():
    while not game.isNextTurn():
        game.receiveAndProcessMessages()

    if game.isMyTurn():
        print('It\'s my turn!\n')
        next_move = -1
        while next_move == -1:
            pawn = getRandomPawn()
            next_move = getRandomMove()
        game.createAndMakeMove(pawn, next_move)

    game.receiveAndProcessMessages()

# def makeMove(pawn, length, lastField):
#     neighbours = session['fields'][pawn]['neighbours']
#     longest_move_length = length`
#     move = -1
#     # foreach neighbour
#         # check if there is a pawn
#         # if not -> return
#         # if yes -> recurrence in that neighbour
#         # return longest move
#     for key, value in neighbours:
#         if session['fields'][value]['player'] is null & length == 0:
#             if longest_move_length < length + 1:
#                 longest_move_length = length + 1
#                 move = value
#         elif session['fields'][value]['player'] is not null & value != lastField:
#             result = makeMove(value, length + 1)
#             if longest_move_length < result[1]:
#                 longest_move_length = result[1]
#                 move = result[0]

#     return (move, longest_move_length)