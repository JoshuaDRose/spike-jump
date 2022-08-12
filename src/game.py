"""
Personal Description:
https://coderslegacy.com/python/pygame-platformer-game-development/

The sort of 'goal' I guess one could say with this sort of project is to try and use object oriented programming
with out making by own sprite class in which to inherit varoius other classes with, but instead to use pygame.sprite.Sprite.

I know several people such as fluffypotato who don't do this at all, but their reasoning is simply 'I never bothered' so I thought I would learn it
Not to say in any way that I'm better than others for using it, in fact more the polar opposite because I prefer to use things that are already done for me.

To give credit where credit is due, another reason dafluffy potato didn't want to use sprites 'and understandably so', is because he's been using pygame for a very long
time and in 1.3 PyGame was when sprites were introduced.

Author: CodersLegacy.com
Date: 2020
"""

import time
import math
import random
import pygame

pygame.display.init()

SIZE = (700, 500)
SCREEN = pygame.display.set_mode(SIZE)
CLOCK = pygame.time.Clock()
FPS = 60
VEC = pygame.math.Vector2
ACC = 0.5
FRIC = -0.12

BLACK     = (0, 0, 0)
WHITE     = (255, 255, 255)
RED       = (255, 0, 0)
GREEN     = (0, 255, 0)
BLUE      = (0, 0, 255)
YELLOW    = (0, 255, 255)
ORANGE    = (255, 165, 0)
PINK      = (255, 192, 203)
PURPLE    = (106, 13, 173)
CYAN      = (0, 255, 255)
MAGENTA   = (255, 0, 255)
GREY      = (124, 124, 124)
DARK_GREY = (16, 16, 16)
GOLDEN    = (255, 215, 0)

running = True

pygame.display.set_caption(f"{__file__} Spike Jump")

# TODO: add docstrings

def radians(x) -> float:
    return x * math.pi / 180


class Particle(object):
    def __init__(self, position):
        x, y = position
        self.x = x
        self.y = y

class Spark(Particle):
    """ Movement sparks that streak behind the player as they 'move' """
    def __init__(self, position):
        Particle.__init__(self, position)
        self.vel = random.randint(0, 20) * 0.01
        self.angle = random.randint(160, 200)
        self.rad = 3
        self.rect = pygame.draw.circle(SCREEN, GOLDEN, (int(round(self.x, 0)), int(round(self.y, 0))), self.rad)
        self.alive = True

    def move(self):
        self.x += math.sin(self.angle) * self.vel
        self.y -= math.cos(self.angle) * self.vel

        self.rect.x = int(round(self.x))
        self.rect.y = int(round(self.y))

    def draw(self):
        pygame.draw.circle(SCREEN, GOLDEN, self.rect.center, self.rad)

    def update(self):
        if self.rad <= 0:
            self.alive = False
        if self.alive:
            self.move()
            self.rad -= 0.05

class Explosion:
    """ Makes and moves particles. (ikr who would have guessed?)"""
    def __init__(self, position):
        x, y = position
        self.x = x
        self.y = y
        self.vel = random.randint(0, 20) * 0.1
        self.angle = random.randint(0, 360)
        self.rad = 3
        self.rect = pygame.draw.circle(SCREEN, YELLOW, (int(round(x, 0)), int(round(y, 0))), self.rad)
        self.alive = True

    def move(self):
        self.x += math.sin(self.angle) * self.vel
        self.y -= math.cos(self.angle) * self.vel

        self.rect.x = int(round(self.x))
        self.rect.y = int(round(self.y))

    def draw(self):
        pygame.draw.circle(SCREEN, YELLOW, self.rect.center, self.rad)

    def collide(self):
        if self.x > SCREEN.get_width() - self.rad:
            self.x = 2 * (SCREEN.get_width() - self.rad) - self.x
            self.angle = -self.angle

        elif self.x < self.rad:
            self.x = 2 * self.rad - self.x
            self.angle = -self.angle

        if self.y > (SCREEN.get_height() - 20) - self.rad:
            self.y = 2 * (SCREEN.get_height() - self.rad) - self.y
            self.angle = math.pi - self.angle

    def update(self):
        if self.rad <= 0:
            self.alive = False

        if self.alive:
            self.move()
            self.collide()
            self.rad -= 0.02


class Text:
    """ Displays text easier """
    def __init__(self, size):
        pygame.font.init()
        self.font = pygame.font.SysFont('impact', size)
        self.alpha = 255
        self.color = list(PURPLE)
        self.color.append(self.alpha)

    def draw(self, center=True):
        SCREEN.blit(self.surf, self.rect)

    def update(self, text, center=True) -> pygame.Surface:
        drawn_text = self.font.render(text, True, self.color, DARK_GREY)
        self.surf = pygame.Surface(self.font.size(text), pygame.SRCALPHA).convert_alpha()
        self.surf.blit(drawn_text, (0, 0))
        self.rect = self.surf.get_rect()
        if center:
            self.rect.center = (SIZE[0] / 2, SIZE[1] / 2)
        return self.surf


class Tilemap:
    """ Regulates the display of tiles """
    pass


class Player(pygame.sprite.Sprite):
    """The player class which will be controlled."""
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((30, 30), pygame.SRCALPHA).convert_alpha()
        self.color = ORANGE
        self.surf.fill(self.color)
        self.rect = self.surf.get_rect(center=(SIZE[0] / 2 - 30 / 2, 420))

        self.drop = False
        self.dead = False
        self.alpha = 255

        self.draw_particles = False
        self.particles = []
        self.death_particles = []
        self.particle_timer = 0
        particle_limit = 15

        self.pos = VEC((SIZE[0] / 2 - self.rect.width / 2, 385))
        self.vel = VEC(0, 0)
        self.acc = VEC(0, 0)

    def move(self):
        """ Allows control of the player """
        self.acc = VEC(0, 0.5)

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[pygame.K_LEFT]:
            self.acc.x = -ACC
        if pressed_keys[pygame.K_RIGHT]:
            self.acc.x = ACC

        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        if self.pos.x > SIZE[0]:
            self.pos.x = 0
        elif self.pos.x < 0:
            self.pos.x = SIZE[0]

        self.rect.midbottom = self.pos

    def jump(self):
        """ Makes the player jump """
        collision = pygame.sprite.spritecollide(self, tiles, False)
        if collision:
            self.vel.y = -15

    def update(self):
        """ Update player physics and collision detection """
        if not self.drop:
            collision = pygame.sprite.spritecollide(player, tiles, False)
            spiked = pygame.sprite.spritecollide(player, spikes, False)
            if player.vel.y > 0:
                if collision:
                    self.pos.y = collision[0].rect.top + 1
                    self.vel.y = 0
                if spiked:
                    self.dead = True
        else:
            self.alpha = 0


class Spike(pygame.sprite.Sprite):
    """ Spikes will kill the player """
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((40, 25), pygame.SRCALPHA).convert_alpha()
        self.rect = self.surf.get_rect()
        self.alpha = 255
        pygame.draw.polygon(self.surf, (124, 124, 124, self.alpha), ((self.rect.bottomleft), (self.rect.midtop), (self.rect.bottomright)))
        self.passed = False
        self.vel = 5
        self.pos = VEC((SIZE[0] + random.randint(50, 200), SIZE[1] - 20))
        self.rect.midbottom = self.pos

    def move(self):
       """ Constant move spike toward the player """
       self.pos -= (self.vel, 0)
       self.rect.midbottom = self.pos

    def update(self):
        """ Detect if collided with anything """
        collision = pygame.sprite.spritecollide(player, spikes, False)
        if collision:
            player.dead = True


class Tile(pygame.sprite.Sprite):
    """Tile class will be for basic platform interaction with entities and particles."""
    def __init__(self, size, pos):
        super().__init__()
        self.surf = pygame.Surface(size, pygame.SRCALPHA).convert_alpha()
        self.color = PINK
        self.center = tuple(i / 2 for i in size)
        self.rect = self.surf.get_rect(center=(self.center))
        self.rect.topleft = pos
        self.alpha = 255

    def update(self):
        self.surf.fill((self.color[0], self.color[1], self.color[2], self.alpha))

    def move(self):
        pass

def explode(position, particles=3) -> list:
    group = []
    for i in range(particles):
        group.append(Explosion(position))
    return group


class Title(Text):
    """ Manages title but with sine wave ^0^ """
    def __init__(self):
        Text.__init__(self, 55)
        self.text = self.update("You Died", center=False)

    def draw(self, dt):
        self.rect.y = (SIZE[1] / 2) - ((self.rect.height /2) + (math.sin(dt * 5) * 6))
        self.rect.x = (SIZE[0] / 2) - (self.rect.width / 2)


game_sprites = pygame.sprite.Group()
tiles = pygame.sprite.Group()
spikes = pygame.sprite.Group()

window_floor = Tile((SIZE[0], 20), (0, SIZE[1] - 20))
player = Player()

game_sprites.add(window_floor)
game_sprites.add(player)

tiles.add(window_floor)

died_text = Title()

score = 0
score_text = Text(70)

doing_explosion = False

overlay = pygame.Surface(SIZE, pygame.SRCALPHA).convert_alpha()
alpha = 0
sprite_alpha = 255

def reset_context():
    """ Reset sprite position, player score, sprite opacity """
    pass

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_UP:
                player.jump()
            if event.key == pygame.K_q:
                running = False
            if event.key == pygame.K_RETURN:
                if player.dead:
                    print("Restarting")
            if event.key == pygame.K_SPACE:
                if player.dead:
                    print("Resarting")
                else:
                    if not player.drop_keytoggle:
                        player.drop = not player.drop
                        player.drop_keytoggle = True

    SCREEN.fill(DARK_GREY)
    player.update()

    if player.dead:
        for index, particle in sorted(enumerate(player.particles), reverse=True):
            player.particles.remove(particle)

        if game_sprites.has(player):
            game_sprites.remove(player)

        if not doing_explosion:
            for particle in explode(player.rect.midright, particles=8):
                player.death_particles.append(particle)
                doing_explosion = True
        for index, particle in sorted(enumerate(player.death_particles), reverse=True):
            particle.update()
            particle.draw()
            if not particle.alive:
                player.death_particles.remove(particle)
        if alpha >= 250 or sprite_alpha <= 5:
            overlay.fill((16, 16, 16))
            died_text.draw(time.time())
            overlay.blit(died_text.surf, died_text.rect)
        else:
            score_text.alpha = 0
            alpha += 2
            sprite_alpha -= 2
            overlay.fill((16, 16, 16, round(alpha)))
            died_text.draw(time.time())
            overlay.blit(died_text.surf, died_text.rect)
            for sprite in game_sprites:
                spike.alpha = sprite_alpha
            for spike in spikes:
                spike.alpha = sprite_alpha

    if score_text.alpha > 0:
        score_text.update(str(score), center=True)
        score_text.draw()

    if alpha < 250:
        for particle in player.particles:
            particle.update()
            particle.draw()

        for particle in player.particles:
            particle.update()
            particle.draw()


        if player.particle_timer == 3:
            if round(player.vel.magnitude()) > 0:
                player.particles.append(Spark(player.rect.midleft))
            player.particle_timer = 0
        player.particle_timer += 1


        if not spikes:
            spike = Spike()
            spikes.add(spike)

        for index, spike in sorted(enumerate(spikes), reverse=True):
            if not player.dead:
                if spike.rect.x < 0 - spike.rect.width:
                    pygame.sprite.Sprite.kill(spike)
                if player.rect.x in range(spike.rect.x, spike.rect.x + spike.rect.width):
                    if not spike.passed:
                        score += 1
                        spike.passed = True

            if spike.rect.x < 0:
                spikes.remove(spike)
                spike = Spike()
                spikes.add(spike)

            spike.update()
            spike.move()
            SCREEN.blit(spike.surf, spike.rect)

        for sprite in game_sprites:
            sprite.move()
            sprite.update()
            SCREEN.blit(sprite.surf, sprite.rect)

    SCREEN.blit(overlay, (0, 0))

    pygame.display.update()
    CLOCK.tick(FPS)

pygame.font.quit()
pygame.display.quit()

