import pygame as py

import random 
import time

FPS = 30
screen_width = 800
screen_height = 600
board_width = 8
board_height = 8
image_size = 64

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

    gems = []
    for i in range(1, 7):
        gem = py.image.load('ele%s.png' %i)
        if gem.get_size()!=(image_size, image_size):
            gem = py.transform.smoothscale(ele, (image_size,image_size))
        gems.append(ele)

    boardRect = []
    for x in range(board_width):
        boardRect.append([])
        for y in range(board_width):
            r =py.Rect((XMARGIN+(x*image_size), YMARGIN+(y*image_size), image_size, image_size))
            boardRect[x].append(r)

def getBlankBoard():
    board = []
    for x in range(board_width):
        board.append([-1]*board_height)
    return board

def fillBoardAndAnimate(board, points, score):
    dropslots = getDropSlots(board)
    while dropslots != [[]]*board_width:
        moving_gems - getDroppingGems(board)
        for x in range(len(dropslots)):
            if len(dropSlots[x])!=0:
                moving_gems.append({})

def runGame():
    gameBoard = getBlankBoard()
    score = 0
    fillBoardAndAnimate(gameboard, [], score)



    
