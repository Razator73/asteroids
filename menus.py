# Asteroids main menu
import csv
import os

import appdirs
import pygame
import pygame.locals as pl

import pygame_textinput
import rungame

scores_file = os.path.join(appdirs.user_data_dir('Asteroids', 'Ryan'), 'highscores.csv')
if not os.path.exists(scores_file):
    os.makedirs(appdirs.user_data_dir('Asteroids', 'Ryan'), exist_ok=True)
    scores = [['Bot1', '100'], ['Bot2', '90'], ['Bot3', '80'], ['Bot4', '70'], ['Bot5', '60']]
    with open(scores_file, 'w', newline='') as file_obj:
        csv.writer(file_obj).writerows(scores)


def main_menu(surf, clock, options):

    choice = 0

    while True:

        surf.fill(rungame.BGCOLOR)
        title_height = 140
        rungame.draw_text(surf, 'ASTEROIDS', 54, int(rungame.WINDOWWIDTH / 3), title_height)
        option_height = title_height + 70
        for option in options:
            rungame.draw_text(surf, option, 24, int(rungame.WINDOWWIDTH / 3), option_height)
            option_height += 30

        box_height = 28
        cursor = pygame.Rect(rungame.WINDOWWIDTH / 3 - 5, title_height + 74 + 30 * choice, 180, box_height)
        pygame.draw.rect(surf, rungame.WHITE, cursor, 2)
        rungame.draw_text(surf, 'version 1.4', 15, 5, rungame.WINDOWHEIGHT - 22)
        pygame.display.update()

        rungame.check_for_quit()

        for event in pygame.event.get():
            if event.type == pl.KEYUP:
                if event.key in (pl.K_a, pl.K_UP):
                    choice = (choice - 1) % len(options)
                elif event.key in (pl.K_s, pl.K_DOWN):
                    choice = (choice + 1) % len(options)
                elif event.key == pl.K_RETURN:
                    return options[choice]

        clock.tick(rungame.FPS)


def draw_score_text(surf, score_name, score_num, height):
    score_text = '{}{}{}'.format(score_name,
                                 '.' * (50 - len(score_name) - len(score_num)),
                                 score_num)
    rungame.draw_text(surf, score_text, 24, int(rungame.WINDOWWIDTH / 6), height, font='courier')


def high_scores(surf, clock, new_score=None):
    with open(scores_file) as f:
        scores_list = list(csv.reader(f))
    textinput = pygame_textinput.TextInput(font_family='courier', text_color=rungame.WHITE,
                                           cursor_color=rungame.WHITE, font_size=24)
    title_height = 60
    if new_score and new_score > int(scores_list[-1][-1]):
        for i in range(len(scores_list)):
            if new_score > int(scores_list[i][1]):
                scores_list.insert(i, ['', str(new_score)])
                scores_list.pop(-1)
                break

        while True:
            surf.fill(rungame.BGCOLOR)
            rungame.draw_text(surf, 'HIGH SCORES', 54, int(rungame.WINDOWWIDTH / 3), title_height)
            score_height = title_height + 110
            events = pygame.event.get()
            for i in range(len(scores_list)):
                if scores_list[i][0] == '':
                    textinput.update(events)
                    rungame.draw_text(surf, 'NEW ---->', 24, 10, score_height - 7)
                    draw_score_text(surf, textinput.get_text(), scores_list[i][1], score_height)
                    surf.blit(textinput.get_surface(), (rungame.WINDOWWIDTH / 6, score_height))
                else:
                    draw_score_text(surf, scores_list[i][0], scores_list[i][1], score_height)
                score_height += 50
            pygame.display.update()

            if pl.K_RETURN in [event.key for event in events if event.type == pl.KEYUP]:
                break
            elif pl.QUIT in [event.type for event in events]:
                exit()
            clock.tick(rungame.FPS)

        scores_list[scores_list.index(['', str(new_score)])][0] = textinput.get_text()
        with open(scores_file, 'w', newline='') as f:
            csv.writer(f).writerows(scores_list)

    surf.fill(rungame.BGCOLOR)
    rungame.draw_text(surf, 'HIGH SCORES', 54, int(rungame.WINDOWWIDTH / 3), title_height)
    score_height = title_height + 110
    for i in range(len(scores_list)):
        draw_score_text(surf, scores_list[i][0], scores_list[i][1], score_height)
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
    menu_options = {'High Scores': high_scores,
                    'Exit': rungame.terminate}

    while True:
        select = main_menu(display_surf, fps_clock, list(menu_options.keys()))
        score = menu_options[select](display_surf, fps_clock)
