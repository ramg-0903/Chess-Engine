#handles input and maintains current game information

import pygame as p
import ChessEngine , ChessAI
import asyncio
from multiprocessing import Process , Queue

WIDTH = HEIGHT = 512    
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MOVE_LOG_PANEL_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250

MAX_FPS = 15 #animation

Images ={}

#creates a dictionary of images that can be accessed by their name
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        Images[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((WIDTH  + MOVE_LOG_PANEL_WIDTH, HEIGHT))
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
    moveLogFont = p.font.SysFont("Arial" , 15 ,False , False)
    playerOne = False #true if player is human and white , if AI is white then false
    playerTwo = True #true if player is human and black , if AI is black then false
    moveUndone = False
    AIThinking = False
    moveFinderProcess = None

    while running:

        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                running = False
            elif e.type == p.MOUSEBUTTONDOWN: #mouse handlers
                if not gameOver:
                    location = p.mouse.get_pos() #(x,y) co-ordinate location of mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row,col) or col >=8: # if the user clicked the same square twice or the move Log
                        sqSelected = ()
                        playerClicks = [] #don't do anything
                    else :
                        sqSelected = (row , col)
                        playerClicks.append(sqSelected)#append both the clicks (it takes two clicks to play a move)
                    if len(playerClicks) == 2 and humanTurn: #after the second click
                        move = ChessEngine.Move(playerClicks[0] , playerClicks[1] , gs.board )
                        #print(move.getChessNotation())
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
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate() #kills the ai process
                        AIThinking = False
                    moveUndone = True
                elif e.key == p.K_e:  # when 'e' is pressed
                    running = False 
                    p.quit()
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected= ()
                    playerClicks = []
                    gameOver = False
                    moveMade = False
                    animate = False
                    if AIThinking:
                        moveFinderProcess.terminate() #kills the ai process
                        AIThinking = False
                    moveUndone = True

#AI Logic

        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:   
                AIThinking = True
                returnQueue = Queue() #used for inter-thread communication and exchange of data
                moveFinderProcess = Process(target=ChessAI.findBestMove , args=(gs , validMoves , returnQueue))
                moveFinderProcess.start()

            if not moveFinderProcess.is_alive():

                AIMove = returnQueue.get() # fetches the data computed by the other thread
                if AIMove is None:
                    AIMove = ChessAI.findRandomMove(validMoves)
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                AIThinking = False
        
        if moveMade :
            if animate:
                animateMoves(gs.moveLog[-1] , screen , gs.board , clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        drawGameState(screen , gs , validMoves , sqSelected, moveLogFont)

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
#        await asyncio.sleep(0)

    
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


def drawGameState(screen , gs , validMoves , sqSelected , moveLogFont):
    drawBoard(screen)
    highlightSquares(screen , gs , validMoves , sqSelected)
    drawPieces(screen , gs.board)
    drawMoveLog(screen , gs , moveLogFont)

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

def drawMoveLog(screen, gs, font):
    
    
    move_log_rect = p.Rect(WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color('black'), move_log_rect)
    move_log = gs.moveLog
    move_texts = []

    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + '. ' + str(move_log[i]) + " "
        if i + 1 < len(move_log):
            move_string += str(move_log[i + 1]) + "  "
        move_texts.append(move_string)

    moves_per_row = 3
    padding = 5
    line_spacing = 2
    text_y = padding

    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]

        text_object = font.render(text, True, p.Color('white'))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing

#asyncio.run(main())
if __name__ == "__main__":
    main()





   






