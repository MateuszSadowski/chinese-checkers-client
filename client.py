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

GAME_ID = 10

player = {
    'id': -1,
    'username': ''
}
session = {
    'start': -1,
    'fields': {},
    'players': [],
    'next_turn': -1
}
game_state = {}

# Create socket and connect
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket successfully created')
except socket.error as err:
    print('Socket creation failed with error {0}'.format(err))

try:
    s.connect((IP, PORT))
    print('Socket successfully connected to {0} on port {1}'.format(IP, PORT))
except socket.error as err:
    print('Socket connection failed with error {0}'.format(err))

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
        print('Received an empty reponse')
        return -1
    print('Received: ' + response)
    messages = response.split('\r\n')
    messages = removeValuesFromList(messages, '')
    return messages

def handlePlayer(msg_info):
    player['id'] = msg_info['id']
    player['username'] = msg_info['username']

def handleInit(msg_info):
    # print(msg_info['session'])
    session['start'] = msg_info['session']['start']
    session['fields'] = msg_info['session']['fields']
    session['players'] = msg_info['session']['players']

def handleTurn(msg_info):
    session['next_turn'] = msg_info['playerID']

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
    else:
        print('Invalid message type')

def handleMessages(messages):
    for msg in messages:
        handleMessage(msg)

def send(msg):
    print('Sending: ' + msg)
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

# def getRandomPawn(player_id):

# Login
username = randomString()
user = {'username': username, 'gameID': GAME_ID}
login_msg = json.dumps(user)

send(login_msg)

messages = receive()
if(messages != -1):
    handleMessages(messages)

# Game start
print('Waiting for game to start...')
messages = receive()
if(messages != -1):
    handleMessages(messages)

processInit(session)

# TODO: write logic to receive next turn always
while(session['next_turn'] == -1):
    messages = receive()
    if(messages != -1):
        handleMessages(messages)
print('Turn of player with id: ')
print(session['next_turn'])

# Wait for turn or make move
while True:
    print('User ID: ')
    print(player["id"])
    if player["id"] == session['next_turn']:
        time.sleep(3)
        print('My move!')
        move = { 'createdAt': datetime.datetime.now().isoformat() + '+00:00', 'oldFieldID': 63, 'newFieldID': 2 }
        # move = { 'oldFieldID': 69, 'newFieldID': 2 }
        move_msg = json.dumps(move)
        send(move_msg)

    messages = receive()
    handleMessages(messages)