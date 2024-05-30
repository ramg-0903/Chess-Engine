#determines game info and valid moves and a log for the moves

class GameState():
    def __init__(self):
        #board is represented by a 2-D list and an empty square is represented by "--"
        self.board=[
                    ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
                    ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
                    ["--", "--", "--", "--", "--", "--", "--", "--"],
                    ["--", "--", "--", "--", "--", "--", "--", "--"],
                    ["--", "--", "--", "--", "--", "--", "--", "--"],
                    ["--", "--", "--", "--", "--", "--", "--", "--"],
                    ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],   
                    ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
                   ]
        
        self.MoveFunctions = {'p':self.getPawnMoves,'B':self.getBishopMoves,'R':self.getRookMoves,
                              'N':self.getKnightMoves,'K':self.getKingMoves,'Q':self.getQueenMoves}

        self.whiteToMove = True
        self.whiteKingLocation = (7,4)#white king's location to see for checks , checkmate and stalemate
        self.blackKingLocation = (0,4)#black king's location
        self.moveLog = []
        self.checkMate = False
        self.staleMate = False
        self.enpassant = () #coordinates of the squares where this is possibile
        self.enpassantPossibleLog = [self.enpassant]
        self.currentCastlingRights = CastleRights(True , True , True , True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks,  self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs , self.currentCastlingRights.bqs )]


    def makeMove(self , move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove #swap player's turn
        #updating king's position
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow , move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow , move.endCol)

        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        #en-passant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'
        
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: #only activates on two square pawn advances
            self.enpassant = ((move.startRow + move.endRow)//2 , move.startCol)
        else:
            self.enpassant = ()

        self.enpassantPossibleLog.append(self.enpassant)

        #updating castle rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks,  self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs , self.currentCastlingRights.bqs ))
        
        #castle move

        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]#moves the rook
                self.board[move.endRow][move.endCol + 1] = '--'#erases the old rook
            else: #queenside castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]#moving the rook
                self.board[move.endRow][move.endCol - 2] = '--'


    def undoMove(self):
        if len(self.moveLog) != 0 :
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove 

            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow , move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow , move.startCol)  

            #undo en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--' #leaving the landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enpassantPossibleLog.pop()
            self.enpassant = self.enpassantPossibleLog[-1]     

            #undo the 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassant = ()

            #undo-ing castle rights
            self.castleRightsLog.pop()
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRights = CastleRights(newRights.wks , newRights.bks , newRights.wqs , newRights.bqs)
            

            #undo the castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'

        self.checkMate = False
        self.staleMate = False
            


    def updateCastleRights(self , move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:#left rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:#right rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow ==0:
                if move.startCol == 0: #left rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:#right rook
                    self.currentCastlingRights.bks = False

        #When Rook is captured
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.bks = False
        

    def getValidMoves(self):
        tempEnpassantPossibile = self.enpassant
        tempCastleRights = CastleRights(self.currentCastlingRights.wks , self.currentCastlingRights.bks,
                                        self.currentCastlingRights.wqs , self.currentCastlingRights.bqs)
        # for each possibile move , play the move and generate all possibile moves of the opponent
        #after this if our king is under attack => Not a valid Move
        moves = self.getAllPossibileMoves()

        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0] , self.whiteKingLocation[1] , moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0] , self.blackKingLocation[1] , moves)

        for i in range(len(moves)-1 ,-1 , -1): #when removing elemnts from a list go backwards
            self.makeMove(moves[i])

            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else :
                self.staleMate = True
        
        else :
            self.checkMate = False
            self.staleMate = False
        
        self.enpassant = tempEnpassantPossibile 
        self.currentCastlingRights = tempCastleRights
        return moves
    

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else :
            return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1]) 


    def squareUnderAttack(self , r, c):
        self.whiteToMove = not self.whiteToMove #switch to opponent's turn
        oppMoves = self.getAllPossibileMoves()
        self.whiteToMove = not self.whiteToMove #switch turns back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: #square is under attack
                return True
        
        return False


    def getAllPossibileMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn=='w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.MoveFunctions[piece](r,c,moves)

        return moves


    def getPawnMoves(self , r , c, moves):
        if self.whiteToMove: #generating white pawn moves
            if self.board[r-1][c] == "--":  #move forward
                moves.append(Move((r,c) , (r-1,c), self.board))
                if r== 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r,c) , (r-2,c), self.board))
            
            if c-1>=0: #capturing to the left
                if self.board[r-1][c-1][0] == "b":
                    moves.append(Move((r,c) , (r-1,c-1), self.board))
                elif (r-1,c-1) == self.enpassant:
                    moves.append(Move((r,c) , (r-1,c-1), self.board , isEnpassantMove= True))
            
            if c+1 <= 7 : #capturing to the right
                if self.board[r-1][c+1][0]=="b":
                    moves.append(Move((r,c) , (r-1,c+1), self.board))
                elif (r-1,c+1) == self.enpassant:
                    moves.append(Move((r,c) , (r-1,c+1), self.board , isEnpassantMove= True))

        else:#black pawn moves
        
            if self.board[r+1][c] == "--":  #move forward
                moves.append(Move((r,c) , (r+1,c), self.board))
                if r== 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r,c) , (r+2,c), self.board))
            
            if c-1>=0: #capturing to the left
                if self.board[r+1][c-1][0] == "w":
                    moves.append(Move((r,c) , (r+1,c-1), self.board))
                elif (r+1,c-1) == self.enpassant:
                    moves.append(Move((r,c) , (r+1,c-1), self.board , isEnpassantMove= True))
            
            if c+1 <= 7 : #capturing to the right
                if self.board[r+1][c+1][0]=="w":
                    moves.append(Move((r,c) , (r+1,c+1), self.board))
                elif (r+1,c+1) == self.enpassant:
                    moves.append(Move((r,c) , (r+1,c+1), self.board , isEnpassantMove= True))
            

    def getBishopMoves(self , r, c, moves):
        directions = ((-1,-1),(-1,1),(1,-1),(1,1))#(-1,0) represents -1 in the x direction and 0 in the y directions == Moving one square up the board
        if self.whiteToMove: enemyColor = 'b' 
        else: enemyColor='w'
        
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] *i
                endCol = c + d[1] *i

                if 0 <= endRow <8 and 0 <= endCol <8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r,c) , (endRow , endCol) , self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r,c) , (endRow , endCol) , self.board))
                        break
                    else: 
                        break
                else:
                    break

    def getKingMoves(self , r, c, moves):
        possibile_spots = ((-1,-1),(-1,0),(-1,1),(0,-1),(1,-1),(1,0),(1,1) , (0,1))
        friendlyColor = 'w' if self.whiteToMove else 'b'

        for i in range(8):
            endRow = r + possibile_spots[i][0]
            endCol = c + possibile_spots[i][1]

            if 0 <= endRow <8 and 0 <= endCol <8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != friendlyColor:
                    moves.append(Move((r,c) , (endRow,endCol) , self.board))

        


    def getCastleMoves(self,r,c,moves):
        if self.squareUnderAttack(r,c):
            return
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks) :
            self.getKingsideCastleMoves(r,c,moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r,c,moves)


    def getKingsideCastleMoves(self,r,c,moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r,c+1) and not self.squareUnderAttack(r,c+2):
                moves.append(Move((r,c) , (r,c+2) , self.board , isCastleMove = True))


    def getQueensideCastleMoves(self,r,c,moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r,c-1) and not self.squareUnderAttack(r,c-2):
                moves.append(Move((r,c) , (r,c-2) , self.board , isCastleMove=True))


    def getQueenMoves(self , r, c, moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)

    def getKnightMoves(self , r, c, moves):
        possibile_spots = ((-2,-1) , (-2,1) , (-1,-2) , (-1,2) , (1,-2) , (1,2) , (2,-1) , (2,1))
        friendlyColor = 'w' if self.whiteToMove else "b"
        for k in possibile_spots:
            endRow = r + k[0]
            endCol = c + k[1]

            if 0<= endRow <=7 and 0<= endCol <=7:
                endPiece = self.board[endRow][endCol]

                if endPiece[0] != friendlyColor:
                    moves.append(Move((r,c) , (endRow,endCol) , self.board))

    def getRookMoves(self , r, c, moves):
        directions = ((-1,0),(0,-1),(1,0),(0,1))#(-1,0) represents -1 in the x direction and 0 in the y directions == Moving one square up the board
        if self.whiteToMove: enemyColor = 'b' 
        else: enemyColor='w'
        
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] *i
                endCol = c + d[1] *i

                if 0 <= endRow <8 and 0 <= endCol <8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r,c) , (endRow , endCol) , self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r,c) , (endRow , endCol) , self.board))
                        break
                    else: 
                        break
                else:
                    break

        
class CastleRights():
    
    def __init__(self , wks , bks , wqs , bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

        
class Move():

    ranksToRows = {"1" : 7 , "2" : 6 ,"3" : 5 ,"4" : 4 ,
                   "5" : 3 ,"6" : 2 ,"7" : 1 ,"8" : 0 }
    rowsToRanks = {v:k for k,v in ranksToRows.items()}

    filesToCols = {"a":0 ,"b":1 ,"c":2 ,"d":3 ,
                   "e":4 ,"f":5 ,"g":6 ,"h":7 }
    colsToFiles = {v:k for k,v in filesToCols.items()}

    def __init__(self , startSq , endSq , board , isEnpassantMove = False , isCastleMove = False):

        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = False

        # pawn promotion
        self.promotionChoice = 'Q'
        if(self.pieceMoved=='wp' and self.endRow == 0) or (self.pieceMoved=='bp' and self.endRow == 7):
            self.isPawnPromotion = True

        #en passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured='wp' if self.pieceMoved== 'bp' else 'bp'

        #castling
        self.isCastleMove = isCastleMove
        
        self.isCapture = self.pieceCaptured != '--'
        self.moveId = self.startRow * 1000 + self.startCol * 100 + self.endRow*10 + self.endCol
        

    
    def __eq__(self,other):
        if isinstance(other , Move):
            return self.moveId == other.moveId
        return False
    
    def __str__(self):

        if self.isCastleMove:     #for all castle moves
            return "o-o" if self.endCol == 6 else "O-O-O"
        
        endSquare = self.getRankFile(self.endRow , self.endCol)

        #pawn moves
        if self.pieceMoved[1] =='p':
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            
            else:
                return endSquare
            
        
        #piece moves
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString+= 'x'
        return moveString + endSquare

    
    def getChessNotation(self):
        return self.getRankFile(self.startRow , self.startCol) + "->" +self.getRankFile(self.endRow , self.endCol)
    
    def getRankFile(self , r , c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
