#!/usr/bin/python

import sys
from math import cos,sin,pi
import pygame as pg

class Environment:
    def __init__(self, ship, destination, stars):
        self.ship = ship
        self.i_ship_x = ship.coord.x
        self.i_ship_y = ship.coord.y
        self.i_ship_th = ship.th
        self.i_ship_vx = ship.vx.raw_v
        self.i_ship_vy = ship.vy.raw_v
        self.dest = destination
        self.stars = stars
    def reset(self):
        ship = Spaceship(self.i_ship_x,
                         self.i_ship_y,
                         self.i_ship_th,
                         self.i_ship_vx,
                         self.i_ship_vy)
        ship.turn_state = self.ship.turn_state
        self.ship = ship

class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def move(self, vx, vy):
        self.x += vx
        self.y += vy
    def get(self):
        return (self.x, self.y)
    def get_distance_squared(self, other_coord):
        other_x,other_y = other_coord.x, other_coord.y
        return (self.x-other_x)**2 + (self.y-other_y)**2

class Velocity:
    def __init__(self, v):
        self.raw_v = v
    def accelerate(self, f):
        self.raw_v += f
    def get(self):
        return self.raw_v

class Spaceship:
    def __init__(self, x, y, th, vx, vy):
        self.coord = Coordinate(x, y)
        self.th = th # ship's rotation in degrees
        self.vx = Velocity(vx)
        self.vy = Velocity(vy)
        self.vth = Velocity(0)
        self.thruster_state = False
        self.thruster_f = 0.02
        self.pic_ship = \
                pg.image.load("graphics/ship.png").convert_alpha()
        self.pic_burning = \
                pg.image.load("graphics/burning.png").convert_alpha()
        self.turn_state = 0
        self.turn_f = 0.2
    def draw(self, screen, trace, tracep=False):
        pic = self.pic_ship
        turnt = pg.transform.rotate(pic, -self.th)
        rect = turnt.get_rect()
        w,h = rect.center
        if tracep:
            x,y = (400,550)
        else:
            x,y = self.coord.get()
        x_trace,y_trace = self.coord.get()
        true_x = x-w
        true_y = y-h
        if self.thruster_state:
            pg.draw.circle(trace,
                           (255, 128, 0),
                           (int(x_trace), int(y_trace)), 1)
        else:
            pg.draw.circle(trace,
                           (255, 0, 0),
                           (int(x_trace), int(y_trace)), 1)
        screen.blit(turnt, (true_x, true_y))
        if self.thruster_state:
            pic_burning = self.pic_burning
            pic_burning = pg.transform.rotate(pic_burning, -self.th)
            th = self.th % 360
            if 0 <= th < 180:
                xcoeff = 24
            else:
                xcoeff = 36
            if 0 <= th < 90 or 270 <= th < 360:
                ycoeff = 36
            else:
                ycoeff = 24
            flame_x = true_x-xcoeff*sin(th*pi/180.)
            flame_y = true_y+ycoeff*cos(th*pi/180.)
            screen.blit(pic_burning, (flame_x, flame_y))
    def collide(self, env):
        if not (0 <= self.coord.x < 800 and 0 <= self.coord.y < 600):
            return 'dead'
        if self.coord.get_distance_squared(env.dest.coord) < env.dest.r**2:
            return 'win'
        for star in env.stars:
            if self.coord.get_distance_squared(star.coord) < star.r**2:
                return 'dead'
        return 'none'
    def physics(self, env):
        if self.thruster_state:
            self.vx.accelerate(self.thruster_f*cos(-pi/2+self.th*pi/180.))
            self.vy.accelerate(self.thruster_f*sin(-pi/2+self.th*pi/180.))
        if self.turn_state != 0:
            self.vth.accelerate(self.turn_state*self.turn_f)
        for star in env.stars:
            strength = star.f/star.coord.get_distance_squared(self.coord)
            denominator = \
                abs(self.coord.x-star.coord.x) + abs(self.coord.y-star.coord.y)
            self.vx.accelerate(-strength*(self.coord.x-star.coord.x)/denominator)
            self.vy.accelerate(-strength*(self.coord.y-star.coord.y)/denominator)
        self.coord.move(self.vx.get(), self.vy.get())
        self.th += self.vth.get()

class Star:
    def __init__(self, x, y, f):
        self.coord = Coordinate(x, y)
        self.f = f
        self.r = int(f/50)
    def draw(self, screen):
        pg.draw.circle(screen, (255, 255, 255), self.coord.get(), self.r)

class Destination:
    def __init__(self, x, y, r):
        self.coord = Coordinate(x, y)
        self.r = r
    def draw(self, screen):
        pg.draw.circle(screen, (0, 255, 0), self.coord.get(), self.r)

pg.init()
pg.display.set_caption("Orbit Racers")
screen = pg.display.set_mode((800, 600))
trace = pg.Surface((800, 600)) #pylint: disable=too-many-function-args
tracep = False
bg = pg.image.load("graphics/bg.png").convert()
levels = [Environment(Spaceship(200, 300, 90, 0, 0),
                      Destination(600, 300, 20),
                      []),
          Environment(Spaceship(200, 300, 90, 0, -2),
                      Destination(600, 300, 20),
                      [Star(400, 300, 1000.)]),
          Environment(Spaceship(200, 300, 90, 0, -2),
                      Destination(700, 300, 20),
                      [Star(400, 300, 1000.)]),
          Environment(Spaceship(735.4, 535.4, 225, -2.6, 2.8),
                      Destination(100, 100, 20),
                      [Star(700, 500, 1000.)]),
          Environment(Spaceship(200, 300, 90, 0, -3.5),
                      Destination(700, 300, 20),
                      [Star(300, 300, 1000.),
                       Star(500, 300, 1000.)]),
          Environment(Spaceship(250, 300, 90, 0, -3.7),
                      Destination(400, 500, 20),
                      [Star(350, 300, 1000.),
                       Star(450, 300, 1500.)]),
          Environment(Spaceship(200, 300, 90, 0, -3.5),
                      Destination(400, 300, 20),
                      [Star(300, 300, 1000.),
                       Star(500, 300, 1000.)]),
          Environment(Spaceship(400, 300, 0, 1.8, -1.8),
                      Destination(400, 100, 25),
                      [Star(250, 300, 1000.),
                       Star(550, 300, 1000.)]),
          Environment(Spaceship(400, 300, 0, 0, 0),
                      Destination(100, 300, 20),
                      [Star(200, 300, 1000.),
                       Star(600, 300, 1000.)]),
          Environment(Spaceship(400, 300, 0, 0, 0),
                      Destination(400, 500, 10),
                      [Star(400, 100, 1000.),
                       Star(100, 300, 1000.),
                       Star(700, 300, 1000.)]),
          Environment(Spaceship(100, 100, 146.31, 0, 0),
                      Destination(700, 500, 25),
                      [Star(100, 500, 1000.),
                       Star(700, 100, 1000.),
                       Star(400, 300, 2000.)]),
          Environment(Spaceship(400, 200, 0, 3, 0),
                      Destination(100, 100, 40),
                      [Star(400, 300, 2000.),
                       Star(150, 300, 1000.),
                       Star(650, 300, 1000.)]),
          Environment(Spaceship(400, 200, 0, 3, 0),
                      Destination(50, 300, 10),
                      [Star(400, 300, 1000.),
                       Star(150, 300, 2500.),
                       Star(650, 300, 2500.)]),
          # Environment(Spaceship(700, 500, 315, -0.47*3., -0.88*3.),
          Environment(Spaceship(657, 469, 315, -0.196*3.744, -0.981*3.744),
                      Destination(614, 157, 10),
                      [Star(186, 157, 500),
                       Star(271, 214, 500),
                       Star(357, 271, 500),
                       Star(443, 329, 500),
                       Star(529, 386, 500),
                       Star(614, 443, 500)]),
          Environment(Spaceship(400, 300, 0, 0, 0),
                      Destination(150, 50, 6),
                      [Star(150, 150, 300.),
                       Star(150, 250, 300.),
                       Star(150, 350, 300.),
                       Star(150, 450, 300.),
                       Star(150, 550, 300.),
                       Star(250, 50, 300.),
                       Star(250, 150, 300.),
                       Star(250, 250, 300.),
                       Star(250, 350, 300.),
                       Star(250, 450, 300.),
                       Star(250, 550, 300.),
                       Star(350, 50, 300.),
                       Star(350, 150, 300.),
                       Star(350, 250, 300.),
                       Star(350, 350, 300.),
                       Star(350, 450, 300.),
                       Star(350, 550, 300.),
                       Star(450, 50, 300.),
                       Star(450, 150, 300.),
                       Star(450, 250, 300.),
                       Star(450, 350, 300.),
                       Star(450, 450, 300.),
                       Star(450, 550, 300.),
                       Star(550, 50, 300.),
                       Star(550, 150, 300.),
                       Star(550, 250, 300.),
                       Star(550, 350, 300.),
                       Star(550, 450, 300.),
                       Star(550, 550, 300.),
                       Star(650, 50, 300.),
                       Star(650, 150, 300.),
                       Star(650, 250, 300.),
                       Star(650, 350, 300.),
                       Star(650, 450, 300.)]),
          Environment(Spaceship(657, 469, 315, 0, 0),
                      Destination(400, 300, 30),
                      [])]
level_i = 0
font = pg.font.Font('graphics/PressStart2P.ttf',
                    21)
level_text = font.render("Level " + str(level_i+1),
                         1,
                         (255,255,255))
env = levels[level_i]
done = False
while not done:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        if event.type == pg.KEYDOWN and event.key == pg.K_TAB:
            tracep = not tracep
        if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            env.ship.thruster_state = True
        if event.type == pg.KEYUP and event.key == pg.K_SPACE:
            env.ship.thruster_state = False
        if event.type == pg.KEYDOWN and event.key == pg.K_LEFT:
            env.ship.turn_state += -1
        if event.type == pg.KEYUP and event.key == pg.K_LEFT:
            env.ship.turn_state -= -1
        if event.type == pg.KEYDOWN and event.key == pg.K_RIGHT:
            env.ship.turn_state += 1
        if event.type == pg.KEYUP and event.key == pg.K_RIGHT:
            env.ship.turn_state -= 1
        if event.type == pg.KEYDOWN and event.key == pg.K_r:
            env.reset()
            trace.fill((0, 0, 0))
            env.ship.turn_state = 0
    env.ship.physics(env)
    screen.blit(bg, (0,0))
    if tracep:
        screen.blit(trace, (0,0))
    screen.blit(level_text, (10,10))
    env.ship.draw(screen, trace, tracep)
    env.dest.draw(screen)
    for star in env.stars:
        star.draw(screen)
    pg.display.flip()
    collision_result = env.ship.collide(env)
    if collision_result == 'dead':
        env.reset()
        trace.fill((0, 0, 0))
    elif collision_result == 'win':
        try:
            level_i += 1
            env = levels[level_i]
            env.reset()
            trace.fill((0, 0, 0))
            level_text = font.render("Level " + str(level_i+1),
                                     1,
                                     (255,255,255))
        except IndexError:
            winner = pg.image.load("graphics/winner.png").convert()
            screen.blit(winner, (0,0))
            time = pg.time.get_ticks()//1000
            time_min = time//60
            time_sec = time%60
            text = font.render(str(time_min)+":"+str(time_sec).zfill(2),
                               1,
                               (255,255,255))
            screen.blit(text, (422, 340))
            pg.display.flip()
            pg.time.delay(10000)
            pg.quit()
            sys.exit()
    pg.time.delay(25)
pg.quit()
