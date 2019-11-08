# an Asteroids clone
# By Ryan Scott
# ver 1.4
import copy
import math
import random

import pygame
import pygame.locals as pl

import rungame

powerup_dict = {'spread-shot': {'label': 'SS', 'life': 300},
                'rapid-fire': {'label': 'RF', 'life': 300},
                'speed-up': {'label': 'SU', 'life': 300},
                'shield': {'label': 'SH', 'life': 30000},
                'piercing-shot': {'label': 'PS', 'life': 300}}


def wrap_center(center):
    if center[0] > rungame.WINDOWWIDTH or center[0] < 0:
        center[0] %= rungame.WINDOWWIDTH
    if center[1] > rungame.WINDOWHEIGHT or center[1] < 0:
        center[1] %= rungame.WINDOWHEIGHT
    return center


class Bullet:
    def __init__(self, ship_shape, direction, ship_velocity=(0, 0)):
        self.center = list(ship_shape[0])
        self.velocity = [rungame.BULLETSPEED * math.cos(direction) + ship_velocity[0],
                         rungame.BULLETSPEED * math.sin(direction) + ship_velocity[1]]
        self.life = 0
        self.line = [self.center, self.center]

    def move(self):
        old_center = copy.copy(self.center)
        self.center[0] += self.velocity[0]
        self.center[1] += self.velocity[1]

        self.line = [self.center, old_center]
        x_df = self.line[1][0] - self.center[0]
        y_df = self.line[1][1] - self.center[1]

        if self.center[0] > rungame.WINDOWWIDTH or self.center[0] < 0:
            self.center[0] %= rungame.WINDOWWIDTH
            self.line = [self.center, [self.center[0] + x_df, self.line[1][1]]]
        if self.center[1] > rungame.WINDOWHEIGHT or self.center[1] < 0:
            self.center[1] %= rungame.WINDOWHEIGHT
            self.line = [self.center, [self.line[1][0], self.center[1] + y_df]]

    def draw(self, surf):
        pygame.draw.circle(surf, rungame.WHITE,
                           [round(self.center[0]), round(self.center[1])],
                           rungame.BULLETSIZE)


class Asteroid:
    def __init__(self, center, radius=None, direction=None, points=None, sub=False, rotated=0):
        self.center = center
        self.radius = radius if radius else random.randint(rungame.ASTEROIDMINSIZE, rungame.ASTEROIDMAXSIZE)
        self.direction = direction if direction else random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(rungame.ASTEROIDMINSPEED, rungame.ASTEROIDMAXSPEED)

        if points:
            self.points = points
        else:
            sides = random.randint(8, 15)
            start_r = random.uniform(0.7, 1.3)
            self.points = [(start_r, 0)]
            for i in range(1, sides):
                self.points.append((random.uniform(0.7, 1.3), 2 * math.pi / sides * i))
            self.points.append((start_r, 0))

        self.rotated = rotated
        self.rotate_speed = random.uniform(-math.pi / 30, math.pi / 30)
        self.sub_asteroids = []
        self.sub = sub

    def draw(self, surf):
        sub_asteroids = []
        pygame.draw.polygon(surf, rungame.WHITE, self.shape(), 4)
        left_collide = right_collide = top_collide = bottom_collide = False
        if not self.sub:
            sides = get_polygon(self.shape())
            if self.radius * 1.4 > self.center[0]:
                for side in sides:
                    if line_collide(side, (rungame.CORNERS[0], rungame.CORNERS[1])):  # collides with left side
                        sub_asteroids.append(Asteroid([self.center[0] + rungame.WINDOWWIDTH, self.center[1]],
                                                      radius=self.radius, points=self.points,
                                                      sub=True, rotated=self.rotated))
                        left_collide = True
            elif self.center[0] > rungame.WINDOWWIDTH - self.radius * 1.4:
                for side in sides:
                    if line_collide(side, (rungame.CORNERS[2], rungame.CORNERS[3])):  # collides with right side
                        sub_asteroids.append(Asteroid([self.center[0] - rungame.WINDOWWIDTH, self.center[1]],
                                                      radius=self.radius, points=self.points,
                                                      sub=True, rotated=self.rotated))
                        right_collide = True
            if self.center[1] > rungame.WINDOWHEIGHT - self.radius * 1.4:
                for side in sides:
                    if line_collide(side, (rungame.CORNERS[1], rungame.CORNERS[2])):  # collides with bottom side
                        sub_asteroids.append(Asteroid([self.center[0], self.center[1] - rungame.WINDOWHEIGHT],
                                                      radius=self.radius, points=self.points,
                                                      sub=True, rotated=self.rotated))
                        bottom_collide = True
            elif self.radius * 1.4 > self.center[1]:
                for side in sides:
                    if line_collide(side, (rungame.CORNERS[3], rungame.CORNERS[0])):  # collides with top side
                        sub_asteroids.append(Asteroid([self.center[0], self.center[1] + rungame.WINDOWHEIGHT],
                                                      radius=self.radius, points=self.points,
                                                      sub=True, rotated=self.rotated))
                        top_collide = True

            if left_collide and bottom_collide:
                sub_asteroids.append(Asteroid([self.center[0] + rungame.WINDOWWIDTH,
                                               self.center[1] - rungame.WINDOWHEIGHT],
                                              radius=self.radius, points=self.points,
                                              sub=True, rotated=self.rotated))
            elif left_collide and top_collide:
                sub_asteroids.append(Asteroid([self.center[0] + rungame.WINDOWWIDTH,
                                               self.center[1] + rungame.WINDOWHEIGHT],
                                              radius=self.radius, points=self.points,
                                              sub=True, rotated=self.rotated))
            elif right_collide and bottom_collide:
                sub_asteroids.append(Asteroid([self.center[0] - rungame.WINDOWWIDTH,
                                               self.center[1] - rungame.WINDOWHEIGHT],
                                              radius=self.radius, points=self.points,
                                              sub=True, rotated=self.rotated))
            elif right_collide and top_collide:
                sub_asteroids.append(Asteroid([self.center[0] - rungame.WINDOWWIDTH,
                                               self.center[1] + rungame.WINDOWHEIGHT],
                                              radius=self.radius, points=self.points,
                                              sub=True, rotated=self.rotated))
            for sub in sub_asteroids:
                sub.draw(surf)

            self.sub_asteroids = sub_asteroids

    def move(self):
        self.center[0] += round(self.speed * math.cos(self.direction))
        self.center[1] += round(self.speed * math.sin(self.direction))
        self.rotated += self.rotate_speed
        self.rotated %= 2 * math.pi

        self.center = wrap_center(self.center)

    def shape(self):
        return [(round(self.radius * pt[0] * math.cos(pt[1] + self.rotated)) + self.center[0],
                 round(self.radius * pt[0] * math.sin(pt[1] + self.rotated)) + self.center[1])
                for pt in self.points]


class Player:
    def __init__(self, center, v=(0, 0), direction=0, sub=False):
        self.center = center
        self.velocity = list(v)
        self.direction = direction
        self.speed = 0
        self.powerups = {'spread-shot':   {'active': False, 'life': 0},  # Spreadshot, time limit
                         'rapid-fire':    {'active': False, 'life': 0},  # Rapid Fire, time limit
                         'speed-up':      {'active': False, 'life': 0},  # Speed up, time limit
                         'shield':        {'active': False, 'life': 0},  # Shield, till hit
                         'piercing-shot': {'active': False, 'life': 0}}  # Piercing Shot, time limit
        self.sub_players = []
        self.sub = sub

    def shape(self):
        """ Gets the desired shape of the ship using the center point and direction """
        tip = (round(self.center[0] + rungame.PLAYERSIZE * math.cos(self.direction)),
               round(self.center[1] + rungame.PLAYERSIZE * math.sin(self.direction)))
        wing1 = (round(self.center[0] + rungame.PLAYERSIZE * math.cos(self.direction - (5 * math.pi / 6))),
                 round(self.center[1] + rungame.PLAYERSIZE * math.sin(self.direction - (5 * math.pi / 6))))
        mid = (round(self.center[0] - rungame.PLAYERSIZE * (math.sqrt(3) / 4) * math.cos(self.direction)),
               round(self.center[1] - rungame.PLAYERSIZE * (math.sqrt(3) / 4) * math.sin(self.direction)))
        wing2 = (round(self.center[0] + rungame.PLAYERSIZE * math.cos(self.direction + (5 * math.pi / 6))),
                 round(self.center[1] + rungame.PLAYERSIZE * math.sin(self.direction + (5 * math.pi / 6))))
        return [tip, wing1, mid, wing2]

    def accelerate(self, acceleration):
        """ Will handle the changing of speed and direction the ship
        flies. Includes a check to see if the speed needs to be normalized
        to the desired top speed while still allowing a direction change. """
        self.velocity[0] += acceleration * math.cos(self.direction)
        self.velocity[1] += acceleration * math.sin(self.direction)
        self.speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)

        if self.speed > rungame.PLAYERTOPSPEED:
            self.velocity[0] = self.velocity[0] / self.speed * rungame.PLAYERTOPSPEED
            self.velocity[1] = self.velocity[1] / self.speed * rungame.PLAYERTOPSPEED
            self.speed = rungame.PLAYERTOPSPEED

    def rotation(self, rotate):
        self.direction += rotate
        self.direction %= 2 * math.pi

    def move(self):
        """ Move the ship based on the velocity. If the ship goes off the screen
        wrap it to the appropriate side"""
        self.center[0] += self.velocity[0]
        self.center[1] += self.velocity[1]

        self.center = wrap_center(self.center)

        for powerup, status in self.powerups.items():
            if status['active']:
                if status['life'] <= powerup_dict[powerup]['life']:
                    status['life'] += 1
                else:
                    status['active'] = False
            
    def draw(self, surf):
        sub_players = []
        pygame.draw.polygon(surf, rungame.WHITE, self.shape())
        if not self.sub:
            if polygon_collide(self.shape(), rungame.CORNERS):  # collides with left side
                sub_players.append(Player([self.center[0] + rungame.WINDOWWIDTH, self.center[1]],
                                          direction=self.direction, sub=True))
                sub_players.append(Player([self.center[0], self.center[1] - rungame.WINDOWHEIGHT],
                                          direction=self.direction, sub=True))
                sub_players.append(Player([self.center[0] + rungame.WINDOWWIDTH, self.center[1] + rungame.WINDOWHEIGHT],
                                          direction=self.direction, sub=True))
                sub_players.append(Player([self.center[0] - rungame.WINDOWWIDTH, self.center[1]],
                                          direction=self.direction, sub=True))
                sub_players.append(Player([self.center[0] - rungame.WINDOWWIDTH, self.center[1] - rungame.WINDOWHEIGHT],
                                          direction=self.direction, sub=True))
                sub_players.append(Player([self.center[0] - rungame.WINDOWWIDTH, self.center[1] + rungame.WINDOWHEIGHT],
                                          direction=self.direction, sub=True))
                sub_players.append(Player([self.center[0], self.center[1] - rungame.WINDOWHEIGHT],
                                          direction=self.direction, sub=True))
                sub_players.append(Player([self.center[0], self.center[1] + rungame.WINDOWHEIGHT],
                                          direction=self.direction, sub=True))
            for sub in sub_players:
                sub.draw(surf)

            if self.powerups['shield']['active']:
                pygame.draw.circle(surf, rungame.WHITE, (round(self.center[0]), round(self.center[1])),
                                   rungame.PLAYERSIZE + 4, 2)
            active_powers = {n: p for n, p in self.powerups.items() if n != 'shield' and p['active']}
            if active_powers:
                pygame.draw.rect(surf, rungame.WHITE, pygame.Rect(0, rungame.WINDOWHEIGHT-60, 150, 60), 0)
                rungame.draw_text(surf, 'Active Powerups', 14, 5, rungame.WINDOWHEIGHT - 55, text_color=rungame.BLACK)
                x = 5
                for active_power, info in active_powers.items():
                    Powerup((x, rungame.WINDOWHEIGHT - 35),
                            active_power,
                            info['life']).draw(surf, powerup_dict[active_power]['life'], 'black')
                    x += 35

            self.sub_players = sub_players


class Powerup:
    def __init__(self, location, type_code, life=0):
        self.location = location
        self.outline = pygame.Rect(location[0], location[1], 30, 30)
        self.life = life
        self.shape = ((location[0], location[1]),
                      (location[0] + 30, location[1]),
                      (location[0] + 30, location[1] + 30),
                      (location[0], location[1] + 30))
        self.type_code = type_code
        self.label = powerup_dict[type_code]['label']

    def draw(self, surf, lifespan=rungame.POWERUPLIFE, color='white'):
        color_fade = max(self.life - lifespan + rungame.FPS * 2, 0)
        if color == 'white':
            powerup_color = (int(abs(255 * math.cos(4 * math.pi / (rungame.FPS * 2) * color_fade))),) * 3
        else:
            powerup_color = (int(abs(255 * math.sin(4 * math.pi / (rungame.FPS * 2) * color_fade))),) * 3
        pygame.draw.rect(surf, powerup_color, self.outline, 2)
        rungame.draw_text(surf, self.label, 16, self.location[0] + 5, self.location[1] + 5,
                          text_color=powerup_color)
        # TODO: add screen wrapping logic
    
    
def polygon_collide(shape1, shape2):
    poly1 = get_polygon(shape1)
    poly2 = get_polygon(shape2)

    for side1 in poly1:
        for side2 in poly2:
            if line_collide(side1, side2):
                return True

    return False


def line_collide(line1, line2):
    o1 = orientation(line1[0], line1[1], line2[0])
    o2 = orientation(line1[0], line1[1], line2[1])
    o3 = orientation(line2[0], line2[1], line1[0])
    o4 = orientation(line2[0], line2[1], line1[1])

    if o1 != o2 and o3 != o4:
        return True

    special_case = ((o1 == 0 and on_segment(line1[0], line2[0], line1[1])) or
                    (o2 == 0 and on_segment(line1[0], line2[1], line1[1])) or
                    (o3 == 0 and on_segment(line2[0], line1[0], line2[1])) or
                    (o4 == 0 and on_segment(line2[0], line1[1], line2[1])))
    if special_case:
        return True

    return False


def get_polygon(shape):
    sides = len(shape)
    return [(shape[i], shape[(i + 1) % sides]) for i in range(sides)]


def on_segment(p, q, r):
    if max(p[0], r[0]) >= q[0] >= min(p[0], r[0]) and max(p[1], r[1]) >= q[1] >= min(p[1], r[1]):
        return True


def orientation(p, q, r):
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    if val == 0:
        return 0
    elif val > 0:
        return 1
    else:
        return 2


def add_asteroid(old_roid=None):
    """ Adds a new asteroid or two if splitting an old one."""
    if old_roid:
        oldsize = old_roid.radius
        oldcenter = old_roid.center
        size1 = random.randint(rungame.ASTEROIDMINSIZE, oldsize - rungame.ASTEROIDMINSIZE)
        size2 = oldsize - size1
        direc1 = (old_roid.direction + random.uniform(math.pi / 36, math.pi / 3)) % (2 * math.pi)
        direc2 = (old_roid.direction - random.uniform(math.pi / 36, math.pi / 3)) % (2 * math.pi)
        center1 = [round(oldcenter[0] + oldsize * math.cos(direc1)),
                   round(oldcenter[1] + oldsize * math.sin(direc1))]
        center2 = [round(oldcenter[0] + oldsize * math.cos(direc2)),
                   round(oldcenter[1] + oldsize * math.sin(direc2))]
        return [Asteroid(center1, size1, direc1),
                Asteroid(center2, size2, direc2)]
    else:
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            center = [random.randint(0, rungame.WINDOWWIDTH - 1), 0]
        elif side == 'bottom':
            center = [random.randint(0, rungame.WINDOWWIDTH - 1), rungame.WINDOWHEIGHT - 1]
        elif side == 'left':
            center = [0, random.randint(0, rungame.WINDOWHEIGHT - 1)]
        else:
            center = [rungame.WINDOWWIDTH - 1, random.randint(0, rungame.WINDOWHEIGHT - 1)]

        return Asteroid(center)


def gameover(surf):
    # add message and option to start over.
    pygame.draw.rect(surf, rungame.BLACK,
                     [int(rungame.WINDOWWIDTH / 4) - 10, int(rungame.WINDOWHEIGHT / 3), 500, 100])
    rungame.draw_text(surf, 'GAME OVER', 48, int(rungame.WINDOWWIDTH / 3), int(rungame.WINDOWHEIGHT / 3))
    rungame.draw_text(surf, 'Press any key to see the high scores', 24,
                      int(rungame.WINDOWWIDTH / 4), int(rungame.WINDOWHEIGHT / 3) + 60)
    pygame.display.update()
    rungame.wait_for_player()


def pause_game(surf):
    rungame.draw_text(surf, 'Game Paused', 48, int(rungame.WINDOWWIDTH / 3), int(rungame.WINDOWHEIGHT / 3))
    rungame.draw_text(surf, 'Press any key to resume', 24, int(rungame.WINDOWWIDTH / 4),
                      int(rungame.WINDOWHEIGHT / 3) + 60)
    pygame.display.update()
    rungame.wait_for_player()


def circle_point_collide(center, radius, point):
    if math.hypot(center[0] - point[0], center[1] - point[1]) < radius:
        return True
    return False


def circle_polygon_collide(center, radius, polygon_shape):
    for i in range(len(polygon_shape) - 1):
        point1 = polygon_shape[i]
        point2 = polygon_shape[i + 1]
        if circle_point_collide(center, radius, point1) or circle_point_collide(center, radius, point2):
            return True
        a = (point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2
        b = 2 * ((point1[0] - point2[0]) * (point2[0] - center[0]) + (point1[1] - point2[1]) * (
                    point2[1] - center[1]))
        c = (point2[0] - center[0]) ** 2 + (point2[1] - center[1]) ** 2 - radius ** 2
        if b ** 2 - 4 * a * c < 0:  # no need to find solutions if they are complex
            return False
        solutions = [(-b + math.sqrt(b ** 2 - 4 * a * c)) / (2 * a), (-b - math.sqrt(b ** 2 - 4 * a * c)) / (2 * a)]
        if (0 <= solutions[0] <= 1) or (0 <= solutions[1] <= 1):  # check real solutions to see if one is in [0, 1]
            return True
    return True


def playgame(game_surf, clock):
    score = 0
    acceleration = 0  # can be 1 to increase 0 stays the same and -1 slow down
    rotate = 0  # similar to acceleration for values, 1 is counter-clockwise, -1 is clockwise, 0 is none
    open_fire = False  # weapon firing or not
    bullet_counter = rungame.FIRERATE  # makes sure bullets don't fire too quickly, instant start could be abused
    bullets = []
    ship = Player([rungame.WINDOWWIDTH / 2, rungame.WINDOWHEIGHT / 2])
    powerups = []
    scorecounter = 0

    asteroids = []
    for i in range(5):
        asteroids.append(add_asteroid())
    asteroidcounter = 0

    game_surf.fill(rungame.BGCOLOR)
    ship.draw(game_surf)
    for obj in asteroids:
        obj.draw(game_surf)
    pygame.display.update()

    while True:  # main game loop
        rungame.check_for_quit()

        for event in pygame.event.get():
            # handle events that aren't going to exit the game
            if event.type == pl.KEYDOWN:
                # handle directional keys
                speed_up_percent = 2 if ship.powerups['speed-up']['active'] else 1
                if event.key in (pl.K_DOWN, pl.K_s):
                    acceleration = -rungame.ACCELERATION / 2 * speed_up_percent
                    # forward thrusters are stronger than reverse thrusters
                elif event.key in (pl.K_UP, pl.K_w):
                    acceleration = rungame.ACCELERATION * speed_up_percent
                elif event.key in (pl.K_RIGHT, pl.K_d):
                    rotate = math.pi / rungame.ROTATESPEED * speed_up_percent
                elif event.key in (pl.K_LEFT, pl.K_a):
                    rotate = -1 * math.pi / rungame.ROTATESPEED * speed_up_percent
                elif event.key == pl.K_SPACE:
                    open_fire = True

            elif event.type == pl.KEYUP:
                if event.key == pl.K_RETURN:
                    pause_game(game_surf)
                elif event.key in (pl.K_UP, pl.K_w, pl.K_DOWN, pl.K_s):
                    acceleration = 0
                elif event.key in (pl.K_RIGHT, pl.K_d, pl.K_LEFT, pl.K_a):
                    rotate = 0
                elif event.key == pl.K_SPACE:
                    open_fire = False

        # handle the ship's speed and rotation
        ship.rotation(rotate)
        ship.accelerate(acceleration)

        # handle the firing of the ship's weapon
        bullet_counter += 1
        add_bullet = (open_fire and
                      (bullet_counter >= rungame.FIRERATE or
                       (bullet_counter >= int(rungame.FIRERATE / 2) and ship.powerups['rapid-fire']['active'])))
        if add_bullet:
            bullets.append(Bullet(ship.shape(), ship.direction, ship.velocity))
            if ship.powerups['spread-shot']['active']:
                bullets.append(Bullet(ship.shape(),
                                      ship.direction + math.radians(rungame.SPREADANGLE), ship.velocity))
                bullets.append(Bullet(ship.shape(),
                                      ship.direction - math.radians(rungame.SPREADANGLE), ship.velocity))
            bullet_counter = 0

        # add new asteroids every so often rate based on score and gets faster as score goes up
        asteroidcounter += 1
        if asteroidcounter >= (rungame.ASTEROIDRATE - int(score / 50)):
            asteroids.append(add_asteroid())
            asteroidcounter = 0

        # move player and objs and increase life time
        ship.move()
        for obj in asteroids + bullets:
            obj.move()
        for obj in bullets + powerups:
            obj.life += 1
        # remove objects above their life time
        bullets = [b for b in bullets if b.life <= rungame.BULLETLIFE]
        powerups = [p for p in powerups if p.life <= rungame.POWERUPLIFE]
        # check for bullet to asteroid collisions
        for b in bullets[:]:
            remove_b = False
            for a in asteroids[:]:
                remove_a = False
                if math.hypot(b.center[0] - a.center[0],
                              b.center[1] - a.center[1]) < rungame.BULLETSIZE + a.radius * 1.7:
                    if math.hypot(b.center[0] - a.center[0],
                                  b.center[1] - a.center[1]) < rungame.BULLETSIZE + a.radius * 0.7:
                        remove_a = remove_b = True
                    else:
                        for side in get_polygon(a.shape()):
                            if line_collide(b.line, side):
                                remove_a = remove_b = True
                                break
                if remove_a:
                    asteroids.remove(a)
                    score += 6 - round(a.radius / 10)
                    if random.uniform(0, 1) >= .95:
                        powerups.append(Powerup(a.center, random.choice(list(powerup_dict.keys()))))
                    if a.radius > rungame.ASTEROIDMINSIZE * 2:
                        asteroids += add_asteroid(a)
            if remove_b and not ship.powerups['piercing-shot']['active']:
                bullets.remove(b)

        # draw all objects onto the surface
        game_surf.fill(rungame.BGCOLOR)
        for obj in asteroids + bullets + powerups:
            obj.draw(game_surf)
        ship.draw(game_surf)

        # add 1 point for each second survived
        scorecounter += 1
        if scorecounter >= 30:
            score += 1
            scorecounter = 0
        pygame.draw.rect(game_surf, rungame.WHITE, pygame.Rect(0, 0, 85, 25), 0)
        rungame.draw_text(game_surf, 'Score: {}'.format(score), 16, 0, 0, text_color=rungame.BLACK)

        # show the new screen
        pygame.display.update()

        # check for player asteroid collisions
        for a in asteroids[:]:
            check_proximity = math.hypot(ship.center[0] - a.center[0],
                                         ship.center[1] - a.center[1]) < rungame.PLAYERSIZE + a.radius * 1.7
            if check_proximity:
                check_shield_collision = (ship.powerups['shield']['active'] and
                                          circle_polygon_collide(ship.center, rungame.PLAYERSIZE + 4, a.shape()))
                if check_shield_collision:
                    asteroids.remove(a)
                    ship.powerups['shield']['active'] = False
                elif polygon_collide(a.shape(), ship.shape()) and not ship.powerups['shield']['active']:
                    gameover(game_surf)
                    return score
        # player collision with a power up
        for p in powerups[:]:
            if polygon_collide(p.shape, ship.shape()):
                powerups.remove(p)
                ship.powerups[p.type_code]['active'] = True
                ship.powerups[p.type_code]['life'] = 0
        clock.tick(rungame.FPS)


if __name__ == '__main__':
    pygame.init()
    fps_clock = pygame.time.Clock()
    display_surf = pygame.display.set_mode((rungame.WINDOWWIDTH, rungame.WINDOWHEIGHT))
    pygame.display.set_caption('Asteroids')
    while True:
        playgame(display_surf, fps_clock)
