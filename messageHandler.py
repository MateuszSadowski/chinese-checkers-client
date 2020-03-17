import json

import helper

ID = 'id'
USERNAME = 'username'
START = 'start'
FIELDS = 'fields'
PLAYERS = 'players'
SESSION = 'session'
PLAYER_ID = 'playerID'
CAUSE = 'cause'
RESULT = 'result'
BOARD = 'board'

class MessageHandler:

    def handleMessage(self, msg, state):
        msg_info = json.loads(msg)
        msg_type = msg_info['type']
        if msg_type == 'player':
            return self.handlePlayer(msg_info, state)
        elif msg_type == 'init':
            return self.handleInit(msg_info, state)
        elif msg_type == 'turn':
            return self.handleTurn(msg_info, state)
        elif msg_type == 'error':
            return self.handleError(msg_info, state)
        elif msg_type == 'result':
            return self.handleResult(msg_info, state)
        elif msg_type == 'info':
            return self.handleInfo(msg_info['info'], state)
        else:
            print('!!ERROR!! Invalid message type')
        
    def handlePlayer(self, msg_info, state):
        state['player'] = {
            ID: msg_info[ID],
            USERNAME: msg_info[USERNAME],
            'total_moves': 0
        }
        print('[INFO] Player logged in with ID: {0} and username: {1}\n'.format(state['player'][ID], state['player'][USERNAME]))
        return state

    def handleInit(self, msg_info, state):
        session_info = msg_info[SESSION];
        state[BOARD] = session_info[FIELDS]
        state[PLAYERS] = session_info[PLAYERS]
        print('[INFO] Game starts!\n')
        return state

    def handleTurn(self, msg_info, state):
        state['next_turn'] = msg_info[PLAYER_ID]
        print('((TURN)) Turn of player with id: {0}\n'.format(state['next_turn']))
        return state

    def handleInfo(self, msg_info, state):
        player = state['player']
        old_field = str(msg_info['oldFieldID'])
        new_field = str(msg_info['newFieldID'])

        state['last_turn'] = state['next_turn']

        # Update player's pawns
        state['pawns'][state['last_turn']] = helper.removeValuesFromList(state['pawns'][state['last_turn']], old_field)
        state['pawns'][state['last_turn']].append(new_field)
        # Update board info
        state['board'][old_field]['player'] = None
        state['board'][new_field]['player'] = state['last_turn']
        print('==MOVE-{3}==> Player {0} made a move from {1} to {2}\n'.format(state['last_turn'], old_field, new_field, player['total_moves']))
        player['total_moves'] += 1
        return state

    def handleError(self, msg_info, state):
        print(msg_info[CAUSE])
        return state

    def handleResult(self, msg_info, state):
        print('==================================================')
        print('<<RESULT>>')
        print('Game ended with result: {0}'.format(msg_info[RESULT]))
        if msg_info[PLAYER_ID] != -1:
            print('for player {1}'.format(msg_info[PLAYER_ID]))
        print('after {0} moves'.format(state['player']['total_moves']))
        print('==================================================')
        state['game_finished'] = True
        return state