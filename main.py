import pygame as py

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

purple = (255,0,255)
lightblue = (170,190,255)
blue = (0,0,255)
red = (255,0,0)
black = (0,0,0)
brown = (85,65,0)

XMARGIN = int((screen_width-image_size*board_width)/2)
YMARGIN = int((screen_height-image_size*board_height)/2)

py.init()

def main():
    global clk, screen, gems, sounds, font
    clk = py.time.Clock()
    screen = py.display.set_mode((screen_width,screen_height))
    py.display.set_caption('game')
    font = py.font.Font('freesansbold.ttf', 36)

    #load images
    gems = []
    for i in range(1, 7):
        gem = py.image.load('gem%s.png' %i)
        if gem.get_size()!=(image_size, image_size):
            gem = py.transform.smoothscale(gem, (image_size,image_size))
        gems.append(gem)
    
    #load sounds
    sounds = {}
    sounds['badswap'] = py.mixer.Sound('badswap.wav')
    sounds['match'] = py.mixer.Sound('match.wav')
    
    #py.Rect objects for each box to do board to pixel coordinate conversion
    boardRect = []
    for x in range(board_width):
        boardRect.append([])
        for y in range(board_width):
            r = py.Rect((XMARGIN+(x*image_size), YMARGIN+(y*image_size), image_size, image_size))
            boardRect[x].append(r)
    
    while True:
        runGame()

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
                if (getGemAt(board, x+pat[0][0], y+pat[0][1]) == 
                    getGemAt(board, x+pat[1][0], y+pat[1][1]) == 
                    getGemAt(board, x+pat[2][0], y+pat[2][1] != None) or 
                    (getGemAt(board, x+pat[0][1], y+pat[0][0]) == 
                    getGemAt(board, x+pat[1][1], y+pat[1][0]) == 
                    getGemAt(board, x+pat[2][1], y+pat[2][0]) != None):
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
    pulDownAllGems(boardCopy)

    dropSlots = []
    for i in range(board_width):
        for y in range(board_height-1, -1, -1):

            if boardCopy[x][y] == -1:
                possibleGems = list(range(len(gems)))
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
                    boardCopy[x][y + offset] = EMPTY_SPACE
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
            pointsSurf = BASICFONT.render(str(pointText['points']), 1, red)
            pointsRect = pointsSurf.get_rect()
            pointsRect.Center = (pointText['x'], pointText['y'])
            screen.blit(pointsSurf, pointsRect)
        pygame.display.update()
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
    while dropSlots != [[]] * BOARDWIDTH:
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
            pygame.draw.rect(screen, black, baordRect[x][y], 1)
            gemToDraw = board[x][y]
            if gemToDraw != -1:
                DISPLAYSURF.blit(gems[gemToDraw], boardRect[x][y])

def getBoardCopyMinusGems(board, gems):
    boardCopy = copy.deepcopy(board)
    for gem in gems:
        if gem['y'] != 'row above board':
            boardCopy[gem['x']][gem['y']] = -1

    return boardCopy

def drawScore(score):
    scoreImg = BASICFONT.render(str(score), 1, SCORECOLOR)
    scoreRect = scoreImg.get_rect()
    scoreRect.bottomleft = (10, screen_height - 6 )
    screen.blit(scoreImg, scoreRect)

def runGame():
    
    
   
