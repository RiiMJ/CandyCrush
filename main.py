import pygame as py
from pygame.locals import *

import random 
import time
import copy

FPS = 30
screen_width = 800
screen_height = 600
board_width = 8
board_height = 8
image_size = 64
moverate = 25
deductspeed = 0.8

purple = (255,0,255)
lightblue = (170,190,255)
blue = (0,0,255)
red = (255,0,0)
black = (0,0,0)
brown = (85,65,0)

XMARGIN = int((screen_width-image_size*board_width)/2)
YMARGIN = int((screen_height-image_size*board_height)/2)

global screen, clk, GEMIMGS, sounds, font, boardRects, GAMESOUNDS

py.init()
screen=py.display.set_mode(screen_width,screen_height)

clk = py.time.Clock()
py.display.set_caption('game')
font = py.font.Font('freensansbold.ttf', 36)

GEMIMGS = []
for i in range(1, 8):
    gemImg = py.image.load('gem%s.png' %i)
    if gemImg.get_size() != (image_size, image_size):
        gemImg = py.transform.smoothscale(gemImg, (image_size, image_size))
        GEMIMGS.append(gemImg)

GAMESOUNDS = {}
GAMESOUNDS['bad swap'] = py.mixer.Sound('badswap.wav')
GAMESOUNDS['match'] = []
for i in range(6):
    GAMESOUNDS['match'].append(py.mixer.Sound('match%s.wav' %i))

boardRects = []
for x in range(board_width):
    boardRects.append([])
    for y in range(board_width):
        r = py.Rect((XMARGIN + (x*image_size), YMARGIN + (y*image_size), image_size, image_size))
        boardRects[x].append(r)

def drawBoard(board):
    for x in range(board_width):
        for y in range(board_height):
            screen.blit(GEMIMGS[], (XMARGIN + (x*image_size), YMARGIN + (y*image_size)))
    
#creates blank board data structure
def getBlankBoard():
    board = []
    for x in range(board_width):
        board.append([-1]*board_height)
    return board

def getSwappingGems(board, firstXY, secondXY):
    gem1 = {'gemNum': board[firstXY['x']][firstXY['y']],
            'x':firstXY['x'], 'y':firstXY['y']}
    gem2 = {'gemNum': board[secondXY['x']][secondXY['y']],
            'x':secondXY['x'], 'y':secondXY['y']}

    if gem1['x'] == gem2['x']+1 and gem1['y'] == gem2['y']:
        gem1['direction'] = 'left'
        gem2['direction'] = 'right'
    elif gem1['x'] == gem2['x']-1 and gem1['y'] == gem2['y']:
        gem1['direction'] = 'right'
        gem2['direction'] = 'left'
    elif gem1['y'] == gem2['y']+1 and gem1['x'] == gem2['x']:
        gem1['direction'] = 'up'
        gem2['direction'] = 'down'
    else:
        return None, None
    
    return gem1, gem2

def getGemAt(board, x, y):
    if x<0 or y<0 or x>=board_width or y>=board_height:
        return None
    else:
        return board[x][y]

def canMakeMove(board):
    oneOffPatterns = (((0,1), (1,0), (2,0)),
    ((0,1), (1,1), (2,0)),
    ((0,0), (1,1), (2,0)),
    ((0,1), (1,0), (2,1)),
    ((0,0), (1,0), (2,1)),
    ((0,0), (1,1), (2,1)),
    ((0,0), (0,2), (0,3)),
    ((0,0), (0,1), (0,3)))
    
    for x in range(board_width):
        for y in range(board_height):
            for pat in oneOffPatterns:
                if  (getGemAt(board, x+pat[0][0], y+pat[0][1]) == 
                    getGemAt(board, x+pat[1][0], y+pat[1][1]) == 
                    getGemAt(board, x+pat[2][0], y+pat[2][1] != None) or 
                    (getGemAt(board, x+pat[0][1], y+pat[0][0]) == 
                    getGemAt(board, x+pat[1][1], y+pat[1][0]) == 
                    getGemAt(board, x+pat[2][1], y+pat[2][0]) != None)):
                    return True    
    return False

def drawMovingGem(gem, progress):
    movex = 0
    movey = 0
    progress*=0.01

    if gem['direction'] == 'up':
        movey = -int(progress*image_size)
    elif gem['direction'] == 'down':
        movey = int(progress*image_size)
    elif gem['direction'] == 'right':
        movex = int(progress*image_size)
    elif gem['direction'] == 'left':
        movex = -int(progress*image_size)
    basex = gem['x']
    basey = gem['y']
    if basey == 'row above board':
        basey = -1

    pixelx = XMARGIN + (basex*image_size)
    pixely = YMARGIN + (basey*image_size)

    r= py.Rect((pixelx+movex, pixely+movey, image_size,image_size))
    screen.blit(image_size[gem['gemNum']], r)

def pullDownAllGems(board):
    for x in range(board_width):
        gems_in_column=[]
        for y in range(board_height):
            if board[x][y]!=-1:
                gems_in_column.append(board[x][y])
        board[x]=([-1]*(board_height-len(gems_in_column)))+gems_in_column

def getDropSlots(board):
    boardCopy = copy.deepcopy(board)
    pullDownAllGems(boardCopy)

    dropSlots = []
    for x in range(board_width):
        for y in range(board_height-1, -1, -1):
            if boardCopy[x][y] == -1:
                possibleGems = list(range(len(GEMIMGS)))
                for offsetX,offsetY in ((0,-1), (1,0), (0,1), (-1,0)):
                    nextGem = getGemAt(boardCopy, x+offsetX, y+offsetY)
                    if nextGem != None and nextGem in possibleGems:
                        possibleGems.remove(nextGem)
                newGem = random.choice(possibleGems)
                boardCopy[x][y] = newGem
                dropSlots[x].append(newGem)
    return dropSlots

def findMatchingGems(board):
    gemsToRemove = []
    boardCopy = copy.deepcopy(board)
    for x in range(board_width):
        for y in range(board_height):
            if getGemAt(boardCopy, x, y) == getGemAt(boardCopy, x+1, y) == getGemAt(boardCopy, x+2, y) and getGemAt(boardCopy, x, y) != -1:
                targetGem = boardCopy[x][y]
                offset = 0
                removeSet = []
                while getGemAt(boardCopy, x + offset, y) == targetGem:
                    removeSet.append((x + offset, y))
                    boardCopy[x + offset][y] = -1
                    offset += 1
                gemsToRemove.apppend(removeSet)
            if getGemAt(boardCopy, x, y) == getGemAt(boardCopy, x, y + 1) == getGemAt(boardCopy, x, y + 2) and getGemAt(boardCopy, x, y) != -1:
                targetGem = boardCopy[x][y]
                offset = 0
                removeSet = []
                while getGemAt(boardCopy, x, y + offset) == targetGem:
                    removeSet.append((x, y + offset ))
                    boardCopy[x][y + offset] = -1
                    offset +=1
                gemsToRemove.append(removeSet)
    return gemsToRemove

def getDroppingGems(board):
    boardCopy = copy.deepcopy(board)
    droppingGems = []
    for x in range(board_width):
        for y in range(board_height - 2, -1, -1):
            if boardCopy[x][y+1] == -1 and boardCopy[x][y] != -1:
                droppingGems.append( {'gemNum': boardCopy[x][y], 'x': x, 'y':y, 'direction':'down'})
                boardCopy[x][y] = -1
    return droppingGems

def animateMovingGems(board, gems, pointsText, score):
    progress = 0
    while progress < 100:
        screen.fill(lightblue)
        drawBoard(board)
        for gem in gems:
            drawMovingGem(gem, progress)
        drawScore(score)
        for pointText in pointsText:
            pointsSurf = font.render(str(pointText['points']), 1, red)
            pointsRect = pointsSurf.get_rect()
            pointsRect.Center = (pointText['x'], pointText['y'])
            screen.blit(pointsSurf, pointsRect)
        py.display.update()
        clk.tick(FPS)
        progress += moverate

def moveGems(board, movingGems):
    for gem in movingGems:
        if gem['y'] != 'row above board':
            board[gem['x']][gem['y']] = -1
            movex = 0
            movey = 0
            if gem['direction'] == 'left':
                movex = -1
            elif gem['direction'] == 'right':
                movex = 1
            elif gem['direction'] == 'down':
                movey = 1
            elif gem['direction'] == 'up':
                movey = -1
            board[gem['x'] + movex][gem['y'] + movey] = gem['gemNum']
        else:
            board[gem['x']][0] = gem['gemNum']

def fillBoardAndAnimate(board, points, score):
    dropSlots = getDropSlots(board)
    while dropSlots != [[]] * board_width:
        movingGems = getDroppingGems(board)
        for x in range(len(dropSlots)):
            if len(dropSlots[x]) != 0:
                movingGems.append({'gemNum': dropSlots[x][0], 'x':x, 'y': 'row above board', 'direction': 'down'})
        boardCopy = getBoardCopyMinusGems(board, movingGems)
        animateMovingGems(boardCopy, movingGems, points, score)
        moveGems(board, movingGems)

        for x in range(len(dropSlots)):
            if len(dropSlots[x]) == 0:
                continue
            board[x][0] = dropSlots[x][0]
            del dropSlots[x][0]

def checkForGemClick(pos):
    for x in range(board_width):
        for y in range(board_height):
            py.draw.rect(screen, black, boardRects[x][y], 1)
            gemToDraw = board[x][y]
            if gemToDraw != -1:
                screen.blit(GEMIMGS[gemToDraw], boardRects[x][y])

def getBoardCopyMinusGems(board, gems):
    boardCopy = copy.deepcopy(board)
    for gem in gems:
        if gem['y'] != 'row above board':
            boardCopy[gem['x']][gem['y']] = -1

    return boardCopy

def drawScore(score):
    scoreImg = font.render(str(score), 1, red)
    scoreRect = scoreImg.get_rect()
    scoreRect.bottomleft = (10, screen_height - 6 )
    screen.blit(scoreImg, scoreRect)

def runGame():
    gameBoard = getBlankBoard()
    score = 0
    fillBoardAndAnimate(gameBoard, [], score)
    firstSelectedGem = None
    lastMouseDownX  = None
    lastMouseDownY = None
    gameIsOver = False
    lastScoreDeduction = time.time()
    clickContinueTextSurf = None

    clickedSpace = None
    for event in py.event.get():
            
        if event.type == KEYUP and event.key == K_BACKSPACE:
            return
        elif event.type == MOUSEBUTTONUP:
            if gameIsOver:
                return
            if event.pos == ( lastMouseDownX, lastMouseDownY):
                clickedSpace = checkForGemClick(event.post)
            else:
                firstSelectedGem = checkForGemClick((lastMouseDownX, lastMouseDownY))
                clickedSpace = checkForGemClick(event.post)
                if not firstSelectedGem or not clickedSpace:
                    firstSelectedGem = None
                    clickedSpace = None
                elif event.type == MOUSEBUTTONDOWN:
                    lastMouseDownX, lastMouseDownY = event.pos
            if clickedSpace and not firstSelectedGem:
                firstSelectedGem = clickedSpace
            elif clickedSpace and firstSelectedGem:
                firstSwappingGem, secondSwappingGem = getSwappingGems(gameBoard, firstSelectedGem, clickedSpace)
                if firstSwappingGem == None and secondSwappingGem == None:
                    firstSelectedGem = None
                    continue
                boardcopy = getBoardCopyMinusGems(gameBoard, firstSwappingGem, secondSwappingGem)
                animateMovingGems(boardcopy, [firstSwappingGem, secondSwappingGem], [], score)
                gameBoard[firstSwappingGem['x']][firstSwappingGem['y']] = firstSwappingGem['imageNum']
                matchedGems = findMatchingGems(gameBoard)
                if matchedGems == []:
                    GAMESOUNDS['bad swap'].play()
                    animateMovingGems(boardcopy, [firstSwappingGem, secondSwappingGem], [], score)
                    gameBoard[firstSwappingGem['x']][firstSwappingGem['y']] = firstSwappingGem['imageNum']
                    gameBoard[secondSwappingGem['x']][secondSwappingGem['y']] = secondSwappingGem['imageNum']
                else:
                    scoreAdd = 0
                    while matchedGems !=[]:
                        points = []
                        for gemSet in matchedGems:
                            scoreAdd += ( 10 + (len(gemSet) - 3 ) * 10 )
                            for gem in gemSet:
                                gameBoard[gem[0]][gem[1]] = -1
                            points.append({'points':scoreAdd,
                                            'x': gem[0] * image_size + XMARGIN,
                                            'y': gem[1] * image_size + YMARGIN})
                            random.choice(GAMESOUNDS['match']).play()
                            score += scoreAdd
                            fillBoardAndAnimate(gameBoard, points, score)
                            matchedGems = findMatchingGems(gameBoard)
                        firstSelectedGems = None
                        if not canMakeMove(gameBoard):
                            gameIsOver = True
        screen.fill(lightblue)
        drawBoard(gameBoard)
        if firstSelectedGem != None:
        py.draw.rect(screen, purple, boardRects[firstSelectedGem['x']][firstSelectedGem['y']], 4)
        if gameIsOver:
            if clickContinueTextSurf == None:
                clickContinueTextSurf = font.render('Final Score: %s(click to continue)' %(score), 1, red, black)
                clickContinueTextRect = clickContinueTextSurf.get_rect()
                clickContinueTextRect.center = int(screen_width / 2 ), int(screen_height / 2)
            screen.blit(clickContinueTextSurf, clickContinueTextRect)
        elif score > 0 and time.time() - lastScoreDeduction > deductspeed:
            score -=1
            lastScoreDeduction = time.time()
        drawScore(score)
        py.display.update()
        clk.tick(FPS)

def main():
    
    while True:
        for event in py.event.get():
            if event.type == QUIT:
                py.quit()
        
    runGame()

if __name__=='__main__':
    main()
