import json
import datetime

import helper
import socketHandler
import messageHandler

class GameController:
    # Refactor
    def makeMove(self, state, oldField, newField, playerId):
        # Update player's pawns
        state['pawns'][playerId] = helper.removeValuesFromList(state['pawns'][playerId], oldField)
        state['pawns'][playerId].append(newField)
        # Update board info
        state['board'][oldField]['player'] = None
        state['board'][newField]['player'] = playerId

        return state

    def incrementTotalMoves(self, state, playerId):
        state['totalMoves'][playerId] += 1

        return state

    def nextTurn(self, state, playerId):
        state['nextTurn'] = playerId

        return state

    def finishTurn(self, state):
        state['lastTurn'] = state['nextTurn']

        return state

    def finishGame(self, state):
        state['gameFinished'] = True

        return state

    # Getters
    def getMyPlayerID(self, state):
        return state['player']['id']

    def getOpponentID(self, state):
        # TODO: refactor
        myPlayerId = state['player']['id']
        for player in state['players']:
            if player['id'] != myPlayerId:
                return player['id']

    def getMyPawns(self, state):
        playerId = self.getMyPlayerID()
        return state['pawns'][playerId]

    def getPlayerPawns(self, playerId):
        return state['pawns'][playerId]

    def getAllPawns(self, state):
        return state['pawns']

    def getCurrentGameState(self, state):
        return state

    def getFieldNeighbours(self, field):
        return state['board'][field]['neighbours']

    def getPawnInField(self, state, field):
        return state['board'][field]['player']

    def getGoalFieldsAndBoundary(self, zoneId):
        if zoneId == 0:
            goalFields = ['91','92','93','94','95','96','97','98','99','100']
            boundary = int(17)
        elif zoneId == 3:
            goalFields = ['61','62','63','64','65','66','67','68','69','70']
            boundary = int(1)

        return goalFields, boundary

    def initializeState(self, state):
        if state['board'] == {}:
            print('!!ERROR!! Board info not initialized')
            return

        for player in state['players']:
            playerId = player['id']
            player['goalFields'], player['boundary'] = self.getGoalFieldsAndBoundary(player['zoneID'])
            state['pawns'][playerId] = []
        
        for key, field in state['board'].items():
            playerId = field['player']
            if playerId is None:
                continue
            state['pawns'][playerId].append(key)

        return state

    # Analyze possible moves
    def analyzeNeighboursForAllPlayerPawns(self, gameState, playerId):
        availableNeighbours = {}
        occupiedNeighbours = {}
        for pawn in gameState['pawns'][playerId]:
            available, occupied = self.analyzeNeighboursForPlayerPawn(gameState, pawn, playerId)
            availableNeighbours[pawn] = available
            occupiedNeighbours[pawn] = occupied

        return availableNeighbours, occupiedNeighbours

    def analyzeNeighboursForPlayerPawn(self, gameState, pawn, playerID): # Analyze direct neighbours
        available = {};
        occupied = {};
        board = gameState['board'];
        for key, neighbour in board[pawn]['neighbours'].items():
            if board[neighbour]['player'] == None:
                available[key] = neighbour
            else:
                occupied[key] = neighbour
        return available, occupied

    def analyzeStep(self, gameState, direction, position): # Analyze bridge of occupied neighbour in specified direction
        board = gameState['board'];
        try:
            possibleBridge = board[position]['neighbours'][direction]
            if board[possibleBridge]['player'] == None:
                return possibleBridge
        except: #Return False if player jumps out of the field
            return None

    def initializeBridge(self, gameState, occupiedNeighbours): # Initialization in order to find all possible bridges
        initialMoves = {}
        for pawn, neighbours in occupiedNeighbours.items():
            initialMoves[pawn] = []
            if len(neighbours) > 0:
                tmp = []
                for direction, neighbour in neighbours.items():
                    fieldToJumpTo = self.analyzeStep(gameState, direction, neighbour)
                    if fieldToJumpTo != None:
                        tmp.append(fieldToJumpTo)
                initialMoves[pawn] = tmp
        return initialMoves

    def nextBridges(self, gameState, occupiedNeigbour): # Step to go from initial bridges the next bridges
        nextBridge = []
        board = gameState['board']
        for direction, nextNeighbour in board[occupiedNeigbour]['neighbours'].items():
            if board[nextNeighbour]['player'] != None:
                fieldToJumpTo = self.analyzeStep(gameState, direction, nextNeighbour)
                if fieldToJumpTo != None:
                    nextBridge.append(fieldToJumpTo)
        return nextBridge

    def allBridges(self, gameState, initialMoves): # Lists of all bridges found, including initial bridges
        for pawn in initialMoves:
            for possibleMove in initialMoves[pawn]:
                tmp = self.nextBridges(gameState, possibleMove)
                for i in tmp:
                    if i not in initialMoves[pawn]:
                        initialMoves[pawn].append(i)
        return initialMoves

    def allMoves(self, gameState, playerID): # Lists of all possible moves including direct and indirect (bridge) moves
        availableNeighbours, occupiedNeighbours = self.analyzeNeighboursForAllPlayerPawns(gameState, playerID)
        initialMoves = self.initializeBridge(gameState, occupiedNeighbours)
        availableBridges = self.allBridges(gameState, initialMoves)
        possibleMoves = {}
        for pawn in availableNeighbours:
            neighbours = availableNeighbours[pawn].values()
            bridges = availableBridges[pawn]
            total = neighbours + bridges
            total.reverse()
            possibleMoves[pawn] = total
            # Remove moves outside goal state if already in goal state
            players = gameState['players']
            for i in range(len(players)):
                if players[i]['id'] == playerID:
                    goalFields = players[i]['goalFields']
                    if pawn in goalFields:
                        possibleMoves[pawn] = [x for x in possibleMoves[pawn] if x in goalFields]
        return possibleMoves