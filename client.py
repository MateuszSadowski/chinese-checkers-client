import socket
import json
import random
import string
import time
import datetime

# RECV_LEN = 4096
RECV_LEN = 10000000
PORT = 8080
IP = 'localhost'

GAME_ID = 37

player = {
    'id': -1,
    'username': '',
    'total_moves': 0
}
session = {
    'start': -1,
    'fields': {},
    'players': [],
    'next_turn': -1,
    'last_turn': -1
}
game_state = {}

# Create socket and connect
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('[INFO] Socket successfully created\n')
except socket.error as err:
    print('!!ERROR!! Socket creation failed with error {0}'.format(err))

try:
    s.connect((IP, PORT))
    print('[INFO] Socket successfully connected to {0} on port {1}\n'.format(IP, PORT))
except socket.error as err:
    print('!!ERROR!! Socket connection failed with error {0}\n'.format(err))

# def receive():
#     response = ''
#     while True:
#         data = s.recv(RECV_LEN)
#         if not data:
#             break
#         response += data
#         messages = response.split('\r\n')
#     return messages

def removeValuesFromList(the_list, val):
   return [value for value in the_list if value != val]

def randomString(stringLength=10):
    # Generate a random string of fixed length
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def receive():
    response = s.recv(RECV_LEN)
    if response == '':
        print('[INFO] Received an empty reponse\n')
        return -1
    # print('-> Received: ' + response + '\n')
    messages = response.split('\r\n')
    messages = removeValuesFromList(messages, '')
    return messages

def handlePlayer(msg_info):
    player['id'] = msg_info['id']
    player['username'] = msg_info['username']
    print('[INFO] Player logged in with ID: {0} and username: {1}\n'. format(player['id'], player['username']))

def handleInit(msg_info):
    session['start'] = msg_info['session']['start']
    session['fields'] = msg_info['session']['fields']
    session['players'] = msg_info['session']['players']
    print('[INFO] Game starts!\n')

def handleTurn(msg_info):
    session['next_turn'] = msg_info['playerID']
    print('((TURN)) Turn of player with id: {0}\n'.format(session['next_turn']))

def handleError(msg_info):
    print(msg_info['cause'])

def handleResult(msg_info):
    print('==================================================')
    print('<<RESULT>> Game ended with result:')
    print('{0} for player {1}'.format(msg_info['result'], msg_info['playerID']))
    print('after {0} moves'.format(total_moves))
    print('==================================================')

def handleInfo(msg_info):
    session['last_turn'] = session['next_turn']
    print('==MOVE-{3}==> Player {0} made a move from {1} to {2}\n'.format(session['last_turn'], msg_info['oldFieldID'], msg_info['newFieldID'], player['total_moves']))
    session['fields'][str(msg_info['oldFieldID'])]['player'] = None
    session['fields'][str(msg_info['newFieldID'])]['player'] = player['id']
    player['total_moves'] += 1

def handleMessage(msg):
    msg_info = json.loads(msg)
    # TODO: implement switch
    # switcher = {
    #     'player': handlePlayer(msg_info)
    # }
    # func = switcher.get(msg_info['type'], lambda: 'Invalid message type')
    # return func
    msg_type = msg_info['type']
    if msg_type == 'player':
        handlePlayer(msg_info)
    elif msg_type == 'init':
        handleInit(msg_info)
    elif msg_type == 'turn':
        handleTurn(msg_info)
    elif msg_type == 'error':
        handleError(msg_info)
    elif msg_type == 'result':
        handleResult(msg_info)
    elif msg_type == 'info':
        handleInfo(msg_info['info'])
    else:
        print('!!ERROR!! Invalid message type')

def handleMessages(messages):
    for msg in messages:
        handleMessage(msg)

def send(msg):
    print('[INFO] Sending: ' + msg + '\n')
    time.sleep(1)
    return s.send(msg)

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
        player_tmp[key] = value['neighbours']

def getRandomPawn(player_id):
    pawns = game_state[player_id]
    return random.choice(list(pawns.keys()))

# def makeMove(pawn, length, lastField):
#     neighbours = session['fields'][pawn]['neighbours']
#     longest_move_length = length
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


# Login
username = randomString()
user = {'username': username, 'gameID': GAME_ID}
login_msg = json.dumps(user)

send(login_msg)

messages = receive()
if(messages != -1):
    handleMessages(messages)

# Game start
print('[INFO] Waiting for game to start...\n')
messages = receive()
if(messages != -1):
    handleMessages(messages)

processInit(session)

# Wait for turn or make move
while True:
    while(session['next_turn'] == session['last_turn']):
        messages = receive()
        if(messages != -1):
            handleMessages(messages)
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

    messages = receive()
    if(messages != -1):
        handleMessages(messages)