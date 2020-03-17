import socket
import json
import random
import string
import time
import datetime

import game
import helper

# RECV_LEN = 4096
GAME_ID = 2

# Create socket and connect


def processInit(session):
    if session['start'] == -1:
        return
    # game_state = {}
    for value in session['players']:
        player_id = value['id']
        game_state[player_id] = {}
    
    for key, value in session['fields'].items():
        if value['player'] is None:
            continue
        player_tmp = game_state[value['player']]
        # TODO: Fix this! Update player pawns after making a move
        player_tmp[key] = value['neighbours']

def getRandomPawn(player_id):
    pawns = game_state[player_id]
    return random.choice(list(pawns.keys()))

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

def getRandomMove(pawn):
    neighbours = session['fields'][str(pawn)]['neighbours']

    for key, value in neighbours.items():
        if session['fields'][value]['player'] is None:
            return value
    
    return -1   # No available moves for this pawn

# Initialize
game = game.Game()
game.connect('localhost', 8080)

# Login
game.login(helper.randomString(), GAME_ID)

# Game start
print('[INFO] Waiting for game to start...\n')
messages = receiveAndSplitMessages()
if(messages != -1):
    handler.handleMessages(messages)

processInit(session)

# Wait for turn or make move
while True:
    while(session['next_turn'] == session['last_turn']):
        messages = receiveAndSplitMessages()
        if(messages != -1):
            handler.handleMessages(messages)
    if player['id'] == session['next_turn']:
        print('Player[{0}]>> It\'s my turn!'.format(player['id']))
        time.sleep(3)
        next_move = -1
        while next_move == -1:
            pawn = getRandomPawn(player['id'])
            next_move = getRandomMove(pawn)
        move = { 'createdAt': datetime.datetime.now().isoformat() + '+00:00', 'oldFieldID': pawn, 'newFieldID': next_move }
        move_msg = json.dumps(move)
        send(move_msg)

    messages = receiveAndSplitMessages()
    if(messages != -1):
        handler.handleMessages(messages)