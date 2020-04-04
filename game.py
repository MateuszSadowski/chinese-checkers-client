import json
import datetime

import helper
import socketHandler
import messageHandler

class Game:
    def __init__(self):  
        self.socketHandler = socketHandler.SocketHandler()
        self.messageHandler = messageHandler.MessageHandler()
        self.game_state = {
            'player': {}, # this player
            'players': [], # info about all players
            'board': {}, # current state of the game
            'pawns': {}, # current pawns location for each player
            'next_turn': -1,
            'last_turn': -1,
            'game_finished': False
        }

    # Getters
    def getMyPlayerID(self):
        return self.game_state['player']['id']

    def getMyPawns(self):
        player_id = self.getMyPlayerID()
        return self.game_state['pawns'][player_id]

    def getPlayerPawns(self, player_id):
        return self.game_state['pawns'][player_id]

    def getAllPawns(self):
        return self.game_state['pawns']

    def getCurrentGameState(self):
        return self.game_state

    def getFieldNeighbours(self, field):
        return self.game_state['board'][field]['neighbours']

    def getPawnInField(self, field):
        return self.game_state['board'][field]['player']

    def isNextTurn(self):
        return self.game_state['next_turn'] != self.game_state['last_turn']

    def isMyTurn(self):
        return self.game_state['next_turn'] == self.game_state['player']['id']

    def isFinished(self):
        return self.game_state['game_finished']

    # Initialize
    def connect(self, ip, port):
        self.socketHandler.connect(ip, port)

    def loginAndWaitToStart(self, username, game_id):
        user = {
            'username': username,
            'gameID': game_id
        }

        login_msg = json.dumps(user)
        self.socketHandler.send(login_msg)

        self.receiveAndProcessMessages()

        print('[INFO] Waiting for game to start...\n')
        self.receiveAndProcessMessages()

    def getGoalFields(self, zone_id):
        if zone_id == 0:
            goalFields = ['91','92','93','94','95','96','97','98','99','100']
            boundary = int(14)
        elif zone_id == 3:
            goalFields = ['61','62','63','64','65','66','67','68','69','70']
            boundary = int(4)

        # TODO: return boundary
        return goalFields

    def initializeState(self):
        if self.game_state['board'] == {}:
            print('!!ERROR!! Board info not initialized')
            return

        for player in self.game_state['players']:
            player_id = player['id']
            player['goalFields'] = self.getGoalFields(player['zoneID'])
            self.game_state['pawns'][player_id] = []
        
        for key, field in self.game_state['board'].items():
            player_id = field['player']
            if player_id is None:
                continue
            self.game_state['pawns'][player_id].append(key)

    # Game
    def createAndMakeMove(self, oldField, newField):
        move = { 
            'createdAt': datetime.datetime.now().isoformat() + '+00:00',
            'oldFieldID': oldField,
            'newFieldID': newField
        }
        move_msg = json.dumps(move)
        self.socketHandler.send(move_msg)

    def receiveAndProcessMessages(self):
        messages = self.socketHandler.receiveAndSplitMessages()
        if(messages != -1):
            for msg in messages:
                self.game_state = self.messageHandler.handleMessage(msg, self.game_state)

    # Analyze possible moves
    def analyzeNeighboursForAllPlayerPawns(self, game_state, player_id):
        availableNeighbours = {}
        occupiedNeighbours = {}
        for pawn in game_state['pawns'][player_id]:
            available, occupied = self.analyzeNeighboursForPlayerPawn(game_state, pawn, player_id)
            availableNeighbours[pawn] = available
            occupiedNeighbours[pawn] = occupied

        return availableNeighbours, occupiedNeighbours

    def analyzeNeighboursForPlayerPawn(self, game_state, pawn, playerID): #Analyze direct neighbours
        available = {};
        occupied = {};
        board = game_state['board'];
        for key, neighbour in board[pawn]['neighbours'].items():
            if board[neighbour]['player'] == None:
                available[key] = neighbour
            else:
                occupied[key] = neighbour
        return available, occupied

    def analyzeStep(self, game_state, direction, position): # Analyze bridge of occupied neighbour in specified direction
        board = game_state['board'];
        try:
            possibleBridge = board[position]['neighbours'][direction]
            if board[possibleBridge]['player'] == None:
                return possibleBridge
        except: #Return False if player jumps out of the field
            return None

    def initializeBridge(self, game_state, occupiedNeighbours): # Initialization in order to find all possible bridges
        initialMoves = {}
        for pawn, neighbours in occupiedNeighbours.items():
            initialMoves[pawn] = []
            if len(neighbours) > 0:
                tmp = []
                for direction, neighbour in neighbours.items():
                    fieldToJumpTo = self.analyzeStep(game_state, direction, neighbour)
                    if fieldToJumpTo != None:
                        tmp.append(fieldToJumpTo)
                initialMoves[pawn] = tmp
        return initialMoves

    def nextBridges(self, game_state, occupiedNeigbour): # Step to go from initial bridges the next bridges
        nextBridge = []
        board = game_state['board']
        for direction, nextNeighbour in board[occupiedNeigbour]['neighbours'].items():
            if board[nextNeighbour]['player'] != None:
                fieldToJumpTo = self.analyzeStep(game_state, direction, nextNeighbour)
                if fieldToJumpTo != None:
                    nextBridge.append(fieldToJumpTo)
        return nextBridge

    def allBridges(self, game_state, initialMoves): # Lists of all bridges found, including initial bridges
        for pawn in initialMoves:
            for possibleMove in initialMoves[pawn]:
                tmp = self.nextBridges(game_state, possibleMove)
                for i in tmp:
                    if i not in initialMoves[pawn]:
                        initialMoves[pawn].append(i)
        return initialMoves

    def allMoves(self, game_state, playerID): # Lists of all possible moves including direct and indirect (bridge) moves
        availableNeighbours, occupiedNeighbours = self.analyzeNeighboursForAllPlayerPawns(game_state, playerID)
        initialMoves = self.initializeBridge(game_state, occupiedNeighbours)
        availableBridges = self.allBridges(game_state, initialMoves)
        possibleMoves = {}
        for pawn in availableNeighbours:
            neighbours = availableNeighbours[pawn].values()
            bridges = availableBridges[pawn]
            possibleMoves[pawn] = neighbours + bridges
            # Remove moves outside goal state if already in goal state
            players = self.game_state['players']
            for i in range(len(players)):
                if players[i]['id'] == playerID:
                    goalFields = players[i]['goalFields']
                    if pawn in goalFields:
                        possibleMoves[pawn] = [x for x in possibleMoves[pawn] if x in goalFields]
        return possibleMoves