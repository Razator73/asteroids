# Asteroids main menu
import rungame
import pygame
import pygame.locals as pl
import csv
import pygame_textinput
import appdirs
import os


scores_file = os.path.join(appdirs.user_data_dir('Asteroids', 'Ryan'), 'highscores.csv')
if not os.path.exists(scores_file):
    os.makedirs(appdirs.user_data_dir('Asteroids', 'Ryan'), exist_ok=True)
    scores = [['Bot1', '100'], ['Bot2', '90'], ['Bot3', '80'], ['Bot4', '70'], ['Bot5', '60']]
    with open(scores_file, 'w', newline='') as file_obj:
        csv.writer(file_obj).writerows(scores)


def main_menu(surf, clock):

    choice = 0

    while True:

        surf.fill(rungame.BGCOLOR)
        title_height = 140
        rungame.draw_text(surf, 'ASTEROIDS', 54, int(rungame.WINDOWWIDTH / 3), title_height)
        options = ['Play Game', 'High Scores', 'Exit']
        option_height = title_height + 70
        for option in options:
            rungame.draw_text(surf, option, 24, int(rungame.WINDOWWIDTH / 3), option_height)
            option_height += 30

        box_height = 28
        cursor = pygame.Rect(rungame.WINDOWWIDTH / 3 - 5, title_height + 74 + 30 * choice, 180, box_height)
        pygame.draw.rect(surf, rungame.WHITE, cursor, 2)
        rungame.draw_text(surf, 'version 1.3', 15, 5, rungame.WINDOWHEIGHT - 22)
        pygame.display.update()

        rungame.check_for_quit()

        for event in pygame.event.get():
            if event.type == pl.KEYUP:
                if event.key in (pl.K_a, pl.K_UP):
                    choice = (choice - 1) % 3
                elif event.key in (pl.K_s, pl.K_DOWN):
                    choice = (choice + 1) % 3
                elif event.key == pl.K_RETURN:
                    return choice

        clock.tick(rungame.FPS)

    # TODO: add selecting the options with mouse cursor


def high_scores(surf, clock, new_score=None):
    with open(scores_file) as file_obj:
        scores = list(csv.reader(file_obj))
    textinput = pygame_textinput.TextInput(font_family='courier', text_color=rungame.WHITE,
                                           cursor_color=rungame.WHITE, font_size=24)
    title_height = 60
    if new_score and new_score > int(scores[-1][-1]):
        for i in range(len(scores)):
            if new_score > int(scores[i][1]):
                scores.insert(i, ['', str(new_score)])
                scores.pop(-1)
                break

        while True:
            surf.fill(rungame.BGCOLOR)
            rungame.draw_text(surf, 'HIGH SCORES', 54, int(rungame.WINDOWWIDTH / 3), title_height)
            score_height = title_height + 110
            events = pygame.event.get()
            for i in range(len(scores)):
                if scores[i][0] == '':
                    textinput.update(events)
                    rungame.draw_text(surf, 'NEW ---->', 24, 10, score_height - 7)
                    score_text = '{}{}{}'.format(textinput.get_text(),
                                                 '.' * (50 - len(textinput.get_text()) - len(str(new_score))),
                                                 scores[i][1])
                    rungame.draw_text(surf, score_text, 24, int(rungame.WINDOWWIDTH / 6), score_height, 'courier')
                    surf.blit(textinput.get_surface(), (rungame.WINDOWWIDTH / 6, score_height))
                else:
                    score_text = '{}{}{}'.format(scores[i][0],
                                                 '.' * (50 - len(scores[i][0]) - len(scores[i][1])),
                                                 scores[i][1])
                    rungame.draw_text(surf, score_text, 24, int(rungame.WINDOWWIDTH / 6), score_height, 'courier')
                score_height += 50
            pygame.display.update()

            if pl.K_RETURN in [event.key for event in events if event.type == pl.KEYUP]:
                break
            elif pl.QUIT in [event.type for event in events]:
                exit()
            clock.tick(rungame.FPS)

        scores[scores.index(['', str(new_score)])][0] = textinput.get_text()
        with open(scores_file, 'w', newline='') as file_obj:
            csv.writer(file_obj).writerows(scores)

    surf.fill(rungame.BGCOLOR)
    rungame.draw_text(surf, 'HIGH SCORES', 54, int(rungame.WINDOWWIDTH / 3), title_height)
    score_height = title_height + 110
    for i in range(len(scores)):
        score_text = '{}{}{}'.format(scores[i][0],
                                     '.' * (50 - len(scores[i][0]) - len(scores[i][1])),
                                     scores[i][1])
        rungame.draw_text(surf, score_text, 24, int(rungame.WINDOWWIDTH / 6), score_height, 'courier')
        score_height += 50
    rungame.draw_text(surf, 'Press any key to go back to the main menu', 24,
                      int(rungame.WINDOWWIDTH / 4), score_height + 75)
    pygame.display.update()
    rungame.wait_for_player()
    return


if __name__ == '__main__':
    pygame.init()
    fps_clock = pygame.time.Clock()
    display_surf = pygame.display.set_mode((rungame.WINDOWWIDTH, rungame.WINDOWHEIGHT))
    pygame.display.set_caption('Asteroids')

    while True:
        select = main_menu(display_surf, fps_clock)
        if select == 1:
            high_scores(display_surf, fps_clock, 81)
        elif select == 2:
            rungame.terminate()
