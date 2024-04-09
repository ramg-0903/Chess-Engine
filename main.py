#handles input and maintains current game information

import pygame as p
import ChessEngine
import asyncio

WIDTH = HEIGHT = 512    
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION

MAX_FPS = 15 #animation

Images ={}

#creates a dictionary of images that can be accessed by their name
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        Images[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


async def main():
    p.init()
    screen = p.display.set_mode((WIDTH , HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves =  gs.getValidMoves()
    moveMade = False #flag variable to indicate when a move has been made
    loadImages()
    running = True
    animate = False #flag variable used while undo-ing a move
    sqSelected = () #keeps track of the last click of the user (tuple)
    playerClicks = [] # keeps track of the player clicks
    gameOver = False

    while running:
        for e in p.event.get():
            if e.type == p.quit:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() #(x,y) co-ordinate location of mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row,col): # if the user clicked the same square twice
                        sqSelected = ()
                        playerClicks = [] #don't do anything
                    else :
                        sqSelected = (row , col)
                        playerClicks.append(sqSelected)#append both the clicks (it takes two clicks to play a move)
                    if len(playerClicks) == 2: #after the second click
                        move = ChessEngine.Move(playerClicks[0] , playerClicks[1] , gs.board )
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = () # reset user clicks
                                playerClicks = []
                            if not moveMade:
                                playerClicks = [sqSelected]
                            
            #keyboard input handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                elif e.key == p.K_e:  # when 'e' is pressed
                    running = False 
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected= ()
                    playerClicks = []
                    moveMade = False
                    animate = False
        
        if moveMade :
            if animate:
                animateMoves(gs.moveLog[-1] , screen , gs.board , clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen , gs , validMoves , sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen , "Black wins by CheckMate")
            else:
                drawText(screen , "White wins by CheckMate")
        elif gs.checkMate:
            gameOver = True
            drawText(screen , "StaleMate")

        clock.tick(MAX_FPS)
        p.display.flip()
        await asyncio.sleep(0)

    
def highlightSquares(screen,gs,validMoves,sqSelected):
    if sqSelected != ():
        r,c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):#square selected is a one that can be moved
        #highlight
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100)#transparency
            s.fill(p.Color(255, 234, 5))
            screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
            #highlight moves starting from that square
            s.fill(p.Color('orange'))
            for move in validMoves:
                if move.startRow == r and move.startCol ==c:
                    screen.blit(s,(move.endCol*SQ_SIZE , move.endRow*SQ_SIZE))


def drawGameState(screen , gs , validMoves , sqSelected):
    drawBoard(screen)
    highlightSquares(screen , gs , validMoves , sqSelected)
    drawPieces(screen , gs.board)

def drawBoard(screen):
    colors = [p.Color(129, 182, 76) , p.Color(246, 255, 227)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen , color , p.Rect(c*SQ_SIZE , r*SQ_SIZE , SQ_SIZE , SQ_SIZE))


def animateMoves(move , screen , board , clock):
    colors = [p.Color(129, 182, 76) , p.Color(246, 255, 227)]
    changeInRow = move.endRow - move.startRow
    changeInCol = move.endCol - move.startCol
    framesPerSqaure = 7#FPS for a single square
    frameCount = (abs(changeInRow) + abs(changeInCol)) * framesPerSqaure

    for frame in range(frameCount + 1):
        r,c = (move.startRow + changeInRow*frame / frameCount , move.startCol + changeInCol*frame / frameCount )
        drawBoard(screen)
        drawPieces(screen , board)
        color = colors[(move.endRow + move.endCol) % 2] # erase the piece moved from its ending square
        endSquare = p.Rect(move.endCol * SQ_SIZE , move.endRow *SQ_SIZE , SQ_SIZE , SQ_SIZE)
        p.draw.rect(screen , color , endSquare)
        if move.pieceCaptured != '--':
            screen.blit(Images[move.pieceCaptured] , endSquare)

        #draw the moving piece
        screen.blit(Images[move.pieceMoved] , p.Rect(c*SQ_SIZE , r*SQ_SIZE , SQ_SIZE , SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen , text):
    font = p.font.SysFont("Helvitca" , 32 ,True , False)
    textObject = font.render(text , 0 , p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2 , HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject , textLocation)
    textObject = font.render(text , 0 ,p.Color("Black"))
    screen.blit(textObject , textLocation.move(2,2))

def drawPieces(screen , board):
   for r in range(DIMENSION):  
       for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(Images[piece] , p.Rect(c*SQ_SIZE , r*SQ_SIZE , SQ_SIZE , SQ_SIZE))

asyncio.run(main())





   






