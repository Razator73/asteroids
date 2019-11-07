import pygame
import pygame.locals as pl
import sys
import math
import os


FPS = 30
WINDOWWIDTH = 960
WINDOWHEIGHT = 540
PLAYERSIZE = 20
PLAYERTOPSPEED = 8
ACCELERATION = .3
ROTATESPEED = math.pi / 18
ASTEROIDMINSPEED = 2
ASTEROIDMAXSPEED = PLAYERTOPSPEED - 1  # player should be able to out run any asteroid
ASTEROIDMINSIZE = 20
ASTEROIDMAXSIZE = 60
ASTEROIDRATE = 40  # higher is slower spawn rate of new astroids
BULLETSIZE = 4
FIRERATE = 7  # lower is faster
BULLETLIFE = 90  # how long before a bullet dies out. Measured in frames
POWERUPLIFE = 210  # how long before a power up disappears. Measured in frames
BULLETSPEED = 12
FONT = 'comicsansms'
SPREADANGLE = 15

# stuck with black and white for now. I'll probably add some more color later
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

BGCOLOR = BLACK

SPEED = 'speed'
CIRCLE = 'circle'
DIREC = 'direction'
LIFE = 'lifetime'
CORNERS = [(0, 0), (0, WINDOWHEIGHT), (WINDOWWIDTH, WINDOWHEIGHT), (WINDOWWIDTH, 0)]


def wait_for_player():
    # used for those times when the player needs to push a button to continue
    keyed_down = False

    while True:
        check_for_quit()

        for event in pygame.event.get():
            if event.type == pl.KEYDOWN and event.type != pl.K_ESCAPE:
                keyed_down = True
            elif event.type == pl.KEYUP and keyed_down:
                return
            if event.type == pl.K_ESCAPE:
                pygame.event.post(event)


def draw_text(surf, text, fontsize, x, y, text_color=WHITE, font=FONT):
    """ draws a text for the given font size at the given x and y """
    font = pygame.font.SysFont(font, fontsize)
    textobj = font.render(text, 1, text_color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surf.blit(textobj, textrect)


def check_for_quit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pl.KEYUP and event.key == pl.K_ESCAPE):
            terminate()
        pygame.event.post(event)


def terminate():
    pygame.quit()
    sys.exit()


def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)


if __name__ == '__main__':
    import menus
    import gameplay

    pygame.init()
    fps_clock = pygame.time.Clock()
    display_surf = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Asteroids')

    while True:
        choice = menus.main_menu(display_surf, fps_clock)
        if choice == 0:
            score = gameplay.playgame(display_surf, fps_clock)
            menus.high_scores(display_surf, fps_clock, score)
        elif choice == 1:
            menus.high_scores(display_surf, fps_clock)
        elif choice == 2:
            terminate()
