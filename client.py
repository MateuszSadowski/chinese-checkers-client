import socket
import json
import random
import string
import time
import datetime

RECV_LEN = 1000000
port = 8080

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.connect(("localhost", port))

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

username = randomString()
game_id = 3

user = {"username": username, "gameID": game_id};
login_msg = json.dumps(user)

print("Sending: " + login_msg)
time.sleep(1)
s.send(login_msg)

login_response = s.recv(RECV_LEN)
print("Recieved: " + login_response)
user_info = json.loads(login_response)
user_id = user_info["id"]

print("Waiting for game to start...")
initial_config = json.loads(s.recv(RECV_LEN))
turn_of_player = json.loads(s.recv(RECV_LEN))

print("Board state: \n")
print(initial_config["session"])
player_id = turn_of_player["playerID"]
print("Turn of player with id: ")
print(player_id)

print("User ID: ")
print(user_id)
if user_id == player_id:
    time.sleep(1)
    print("My move!")
    move = { "createdAt": datetime.datetime.now().isoformat() + "+00:00", "oldFieldID": 92, "newFieldID": 58 }
    # move = { "oldFieldID": 69, "newFieldID": 2 }
    move_msg = json.dumps(move)
    print("Sent: ")
    print(s.send(move_msg))

response = s.recv(RECV_LEN)
print(response)
# next_config = json.loads(s.recv(RECV_LEN))
# next_turn_of_player = json.loads(s.recv(RECV_LEN))

# print("Board state: \n")
# print(next_config["session"])
# player_id = next_turn_of_player["playerID"]
# print("Turn of player with id: " + player_id + "\n")