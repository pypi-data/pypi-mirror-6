from random import betavariate as _b
from time import sleep as _sleep

def randomsleep(scale = 15, alpha = 2, beta = 3):
    _sleep(scale * _b(alpha, beta))
