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
        gem = py.image.load('ele%s.png' %i)
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

    gem1 = {'gemNum': board[firstXY['x']][fistXY['y']],
            'x':firstXY['x'], 'y':firstXY['y']}
    gem2 = {'gemNum': board[secondXY['x']][secondXY['y']],
            'x':secondXY['x'], 'y':secondXY['y']}

    if gem1['x'] == gem2['x']+1 and gem1['y'] == gem2['y']:
        gem1['direction'] = 'left'
        gem2['direction'] = 'right'
    elif gem1['x'] == gem2['x']-1 and gem1['y'] == gem2['y']:
        gem1['direction'] = 'right'
        gem2['direction'] = 'left'
    elif gem1['y'] == gem2['y']+1 and gem1['x'] == ge2['x']:
        gem1['direction'] = 'up'
        gem2['direction'] = 'down'
    else:
        return None, None
    
    return gem1, gem2

