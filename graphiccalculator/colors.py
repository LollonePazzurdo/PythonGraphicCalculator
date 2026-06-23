import random

BLUE = 255,0,0
BLACK = 0,0,0
CYAN = 255,255,0
GREEN = 0,128,0
GRAY = 128,128,128
LIGHTBLUE = 255,128,0
LIME = 0,255,0
ORANGE = 0,128,255
PINK = 255,0,255
PURPLE = 255,0,128
RED = 0,0,255
WHITE = 255,255,255
YELLOW = 0,255,255

def r_color():
    return (random.randint(0,255), random.randint(0,255), random.randint(0,255))