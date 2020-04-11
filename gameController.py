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

    def setWonGame(self, state):
        state['gameWon'] = True

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
            neighbours = list(availableNeighbours[pawn].values())
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
        
    # Visualization
    def drawField(self, state, number):
        board = state['board']
        maxPlayer = self.getMyPlayerID(state)
        minPlayer = self.getOpponentID(state)
        if number == None:
            return '        '
        elif number == 'mid':
            return '    '
        elif number == 'start':
            return '      '
        elif board[str(number)]['player'] == maxPlayer:
            if len(str(number)) == 1:
                return '\u001b[32m| '+str(number)+' |(*)\u001b[0m'
            elif len(str(number)) == 2:
                return '\u001b[32m| '+str(number)+'|(*)\u001b[0m'
            else:
                return '\u001b[32m|'+str(number)+'|(*)\u001b[0m'
        elif board[str(number)]['player'] == minPlayer:
            if len(str(number)) == 1:
                return '\u001b[35m| '+str(number)+' |(#)\u001b[0m'
            elif len(str(number)) == 2:
                return '\u001b[35m| '+str(number)+'|(#)\u001b[0m'
            else:
                return '\u001b[35m|'+str(number)+'|(#)\u001b[0m'
        else:
            if len(str(number)) == 1:
                return '| '+str(number)+' |( )'
            elif len(str(number)) == 2:
                return '| '+str(number)+'|( )'
            else:
                return '|'+str(number)+'|( )'

    def printBoard(self, state):
        print(self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,70))
        print("")
        print("")
        print(self.drawField(state,'start')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,69)+self.drawField(state,'mid')+self.drawField(state,68))
        print("")
        print("")
        print(self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,67)+self.drawField(state,'mid')+self.drawField(state,66)+self.drawField(state,'mid')+self.drawField(state,65))
        print("")
        print("")
        print(self.drawField(state,'start')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,64)+self.drawField(state,'mid')+self.drawField(state,63)+self.drawField(state,'mid')+self.drawField(state,62)+self.drawField(state,'mid')+self.drawField(state,61))
        print("")
        print("")
        print(self.drawField(state,80)+self.drawField(state,'mid')+self.drawField(state,78)+self.drawField(state,'mid')+self.drawField(state,75)+self.drawField(state,'mid')+self.drawField(state,71)+self.drawField(state,'mid')+self.drawField(state,4)+self.drawField(state,'mid')+self.drawField(state,3)+self.drawField(state,'mid')+self.drawField(state,2)+self.drawField(state,'mid')+self.drawField(state,1)+self.drawField(state,'mid')+self.drawField(state,0)+self.drawField(state,'mid')+self.drawField(state,114)+self.drawField(state,'mid')+self.drawField(state,117)+self.drawField(state,'mid')+self.drawField(state,119)+self.drawField(state,'mid')+self.drawField(state,120))
        print("")
        print("")
        print(self.drawField(state,'start')+self.drawField(state,79)+self.drawField(state,'mid')+self.drawField(state,76)+self.drawField(state,'mid')+self.drawField(state,72)+self.drawField(state,'mid')+self.drawField(state,10)+self.drawField(state,'mid')+self.drawField(state,9)+self.drawField(state,'mid')+self.drawField(state,8)+self.drawField(state,'mid')+self.drawField(state,7)+self.drawField(state,'mid')+self.drawField(state,6)+self.drawField(state,'mid')+self.drawField(state,5)+self.drawField(state,'mid')+self.drawField(state,113)+self.drawField(state,'mid')+self.drawField(state,116)+self.drawField(state,'mid')+self.drawField(state,118))
        print("")
        print("")
        print(self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,77)+self.drawField(state,'mid')+self.drawField(state,73)+self.drawField(state,'mid')+self.drawField(state,17)+self.drawField(state,'mid')+self.drawField(state,16)+self.drawField(state,'mid')+self.drawField(state,15)+self.drawField(state,'mid')+self.drawField(state,14)+self.drawField(state,'mid')+self.drawField(state,13)+self.drawField(state,'mid')+self.drawField(state,12)+self.drawField(state,'mid')+self.drawField(state,11)+self.drawField(state,'mid')+self.drawField(state,112)+self.drawField(state,'mid')+self.drawField(state,115))
        print("")
        print("")
        print(self.drawField(state,'start')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,74)+self.drawField(state,'mid')+self.drawField(state,25)+self.drawField(state,'mid')+self.drawField(state,24)+self.drawField(state,'mid')+self.drawField(state,23)+self.drawField(state,'mid')+self.drawField(state,22)+self.drawField(state,'mid')+self.drawField(state,21)+self.drawField(state,'mid')+self.drawField(state,20)+self.drawField(state,'mid')+self.drawField(state,19)+self.drawField(state,'mid')+self.drawField(state,18)+self.drawField(state,'mid')+self.drawField(state,111))
        print("")
        print("")
        print(self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,34)+self.drawField(state,'mid')+self.drawField(state,33)+self.drawField(state,'mid')+self.drawField(state,32)+self.drawField(state,'mid')+self.drawField(state,31)+self.drawField(state,'mid')+self.drawField(state,30)+self.drawField(state,'mid')+self.drawField(state,29)+self.drawField(state,'mid')+self.drawField(state,28)+self.drawField(state,'mid')+self.drawField(state,27)+self.drawField(state,'mid')+self.drawField(state,26))
        print("")
        print("")
        print(self.drawField(state,'start')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,81)+self.drawField(state,'mid')+self.drawField(state,42)+self.drawField(state,'mid')+self.drawField(state,41)+self.drawField(state,'mid')+self.drawField(state,40)+self.drawField(state,'mid')+self.drawField(state,39)+self.drawField(state,'mid')+self.drawField(state,38)+self.drawField(state,'mid')+self.drawField(state,37)+self.drawField(state,'mid')+self.drawField(state,36)+self.drawField(state,'mid')+self.drawField(state,35)+self.drawField(state,'mid')+self.drawField(state,104))
        print("")
        print("")
        print(self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,85)+self.drawField(state,'mid')+self.drawField(state,82)+self.drawField(state,'mid')+self.drawField(state,49)+self.drawField(state,'mid')+self.drawField(state,48)+self.drawField(state,'mid')+self.drawField(state,47)+self.drawField(state,'mid')+self.drawField(state,46)+self.drawField(state,'mid')+self.drawField(state,45)+self.drawField(state,'mid')+self.drawField(state,44)+self.drawField(state,'mid')+self.drawField(state,43)+self.drawField(state,'mid')+self.drawField(state,103)+self.drawField(state,'mid')+self.drawField(state,107))
        print("")
        print("")
        print(self.drawField(state,'start')+self.drawField(state,88)+self.drawField(state,'mid')+self.drawField(state,86)+self.drawField(state,'mid')+self.drawField(state,83)+self.drawField(state,'mid')+self.drawField(state,55)+self.drawField(state,'mid')+self.drawField(state,54)+self.drawField(state,'mid')+self.drawField(state,53)+self.drawField(state,'mid')+self.drawField(state,52)+self.drawField(state,'mid')+self.drawField(state,51)+self.drawField(state,'mid')+self.drawField(state,50)+self.drawField(state,'mid')+self.drawField(state,102)+self.drawField(state,'mid')+self.drawField(state,106)+self.drawField(state,'mid')+self.drawField(state,109))
        print("")
        print("")
        print(self.drawField(state,90)+self.drawField(state,'mid')+self.drawField(state,89)+self.drawField(state,'mid')+self.drawField(state,87)+self.drawField(state,'mid')+self.drawField(state,84)+self.drawField(state,'mid')+self.drawField(state,60)+self.drawField(state,'mid')+self.drawField(state,59)+self.drawField(state,'mid')+self.drawField(state,58)+self.drawField(state,'mid')+self.drawField(state,57)+self.drawField(state,'mid')+self.drawField(state,56)+self.drawField(state,'mid')+self.drawField(state,101)+self.drawField(state,'mid')+self.drawField(state,105)+self.drawField(state,'mid')+self.drawField(state,108)+self.drawField(state,'mid')+self.drawField(state,110))
        print("")
        print("")
        print(self.drawField(state,'start')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,91)+self.drawField(state,'mid')+self.drawField(state,92)+self.drawField(state,'mid')+self.drawField(state,93)+self.drawField(state,'mid')+self.drawField(state,94))
        print("")
        print("")
        print(self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,95)+self.drawField(state,'mid')+self.drawField(state,96)+self.drawField(state,'mid')+self.drawField(state,97))
        print("")
        print("")
        print(self.drawField(state,'start')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,98)+self.drawField(state,'mid')+self.drawField(state,99))
        print("")
        print("")
        print(self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,None)+self.drawField(state,'mid')+self.drawField(state,100))
