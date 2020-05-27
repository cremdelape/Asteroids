from conf import *
import pygame
import random

vec = pygame.math.Vector2


# Teleports the enemy back into the screen
def teleport(obj):
    # X axis
    if obj.pos.x + obj.radius < 0:
        obj.pos.x = WIDTH + obj.radius
    if obj.pos.x > WIDTH + obj.radius:
        obj.pos.x = -obj.radius
    # Y axis
    if obj.pos.y + obj.radius < 0:
        obj.pos.y = HEIGHT + obj.radius
    if obj.pos.y > HEIGHT + obj.radius:
        obj.pos.y = -obj.radius


# noinspection PyArgumentList
class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        image = pygame.image.load('gallery/sprites/player_ship.png')
        # self.image_org = pygame.transform.scale(image, (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image_org = image
        self.image = self.image_org.copy()
        self.rect = self.image.get_rect()
        self.radius = PLAYER_WIDTH // 2
        self.pos = vec(WIDTH // 2, HEIGHT // 2)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rot = 0
        self.rect.center = self.pos
        self.mouse = vec(0, 0)
        self.health = 100
        self.juice = 100
        self.score = 0
        self.last_fire = pygame.time.get_ticks()
        self.last_drink = pygame.time.get_ticks()
        self.cooldown = COOL_DOWN
        self.game = game
        self.streak = 0
        self.laser_count = 1

    def input(self):
        self.acc = vec(0, 0)
        move = pygame.mouse.get_pressed()
        if move[0]:
            self.acc = vec(PLAYER_ACC, 0).rotate(-self.rot)

    def shoot(self):
        move = pygame.mouse.get_pressed()
        now = pygame.time.get_ticks()
        if now - self.last_fire > self.cooldown and move[2] and self.juice > 10:
            if self.laser_count in [1, 3, 5]:
                self.game.lasers.add(Laser(self.game, self.rot))
            if self.laser_count in [2, 3, 4, 5]:
                self.game.lasers.add(Laser(self.game, self.rot + SPREAD))
                self.game.lasers.add(Laser(self.game, self.rot - SPREAD))
            if self.laser_count in [4, 5]:
                self.game.lasers.add(Laser(self.game, self.rot + 2 * SPREAD))
                self.game.lasers.add(Laser(self.game, self.rot - 2 * SPREAD))
            self.acc = vec(KNOCK_BACK - self.laser_count, 0).rotate(-self.rot)

            self.last_fire = now
            self.juice -= COST

            if self.juice < 0:
                self.juice = 0

    def update(self):
        # Setting the laser count
        if self.streak > 4 * LASER_JUMP:
            self.laser_count = 5
        elif self.streak > 3 * LASER_JUMP:
            self.laser_count = 4
        elif self.streak > 2 * LASER_JUMP:
            self.laser_count = 3
        elif self.streak > 1 * LASER_JUMP:
            self.laser_count = 2
        else:
            self.laser_count = 1

        # Refilling the juice
        now = pygame.time.get_ticks()
        if now - self.last_drink > 1:
            self.juice += INCREASE
            self.last_drink = now
        if self.juice > 100:
            self.juice = 100
        self.input()
        self.shoot()
        # Turning the ship towards the mouse
        self.mouse = pygame.mouse.get_pos()
        self.rot = (self.mouse - self.pos).angle_to(vec(1, 0))
        self.image = self.image_org.copy()
        self.image = pygame.transform.rotate(self.image, self.rot)
        self.rect = self.image.get_rect()
        # Applying friction
        self.acc.x += self.vel.x * FRICTION
        self.acc.y += self.vel.y * FRICTION
        # Laws of motion
        self.vel += self.acc
        self.pos += self.vel
        teleport(self)
        self.rect.center = self.pos


# noinspection PyArgumentList
class Laser(pygame.sprite.Sprite):
    def __init__(self, game, rot):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.rot = rot
        self.image_org = pygame.image.load('gallery/sprites/laser.png')
        self.image = pygame.transform.rotate(self.image_org, self.rot)
        self.rect = self.image.get_rect()
        self.pos = vec(self.game.player.pos.x, self.game.player.pos.y)
        self.rect.center = self.pos
        self.vel = vec(LASER_SPEED, 0).rotate(-self.rot)
        self.miss = False
        pygame.mixer.Sound(random.choice(LASER_SOUND)).play()

    def boundary(self):
        if not 0 < self.pos.x < WIDTH:
            self.kill()
            self.game.player.streak -= max(1, int(self.game.player.streak * 0.1))
        if not 0 < self.pos.y < HEIGHT:
            self.kill()
            self.game.player.streak -= max(1, int(self.game.player.streak * 0.1))

    def update(self):

        self.pos += self.vel
        self.rect.center = self.pos
        self.boundary()


# noinspection PyArgumentList
class Asteroid(pygame.sprite.Sprite):
    def __init__(self, game, size, spawn, vel):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.size = size
        image = random.choice(self.size)
        self.image_org = pygame.image.load(image)
        self.image = self.image_org.copy()
        self.radius = self.image.get_size()[1] // 2
        self.rect = self.image.get_rect()
        self.hit_box = self.image_org.get_rect()
        self.spawn = spawn
        self.pos = vec(self.spawn)
        self.rect.center = self.pos
        self.vel = vel
        self.rot = 0
        self.rot_speed = random.randrange(-ROT_SPEED, ROT_SPEED)

    def break_of(self):
        if self.size == SMALL:
            self.game.player.score += 5
            self.kill()
        if self.size == MEDIUM:
            vel1 = self.vel.rotate(DISPERSE)
            vel2 = self.vel.rotate(-DISPERSE)
            self.game.asteroids.add(Asteroid(self.game, SMALL, self.pos, vel1))
            self.game.asteroids.add(Asteroid(self.game, SMALL, self.pos, vel2))
            self.game.player.score += 10
            self.kill()
        if self.size == BIG:
            vel1 = self.vel.rotate(DISPERSE)
            vel2 = self.vel.rotate(-DISPERSE)
            self.game.asteroids.add(Asteroid(self.game, MEDIUM, self.pos, vel1))
            self.game.asteroids.add(Asteroid(self.game, MEDIUM, self.pos, vel2))
            self.game.player.score += 15
            self.kill()

    def update(self):
        # Spinning
        self.image = self.image_org.copy()
        self.rot += self.rot_speed
        self.image = pygame.transform.rotate(self.image, self.rot)
        self.rect = self.image.get_rect()
        self.hit_box = self.image_org.get_rect()

        self.pos += self.vel
        teleport(self)
        self.rect.center = self.pos
        self.hit_box.center = self.pos


# noinspection PyArgumentList
class Meteor(pygame.sprite.Sprite):
    def __init__(self, game, size, spawn, vel):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.size = size
        image = random.choice(self.size)
        self.image_org = pygame.image.load(image)
        self.image = self.image_org.copy()
        self.radius = self.image_org.get_size()[1] // 2
        self.rect = self.image.get_rect()
        self.hit_box = self.image_org.get_rect()
        self.spawn = spawn
        self.pos = vec(self.spawn)
        self.rect.center = self.pos
        self.vel = vel
        self.rot = 0
        self.rot_speed = random.randrange(-ROT_SPEED, ROT_SPEED)
        teleport(self)

    def boundary(self):
        if self.pos.x + self.radius < 0:
            self.kill()
        if self.pos.x > WIDTH + self.radius:
            self.kill()
        # Y axis
        if self.pos.y + self.radius < 0:
            self.kill()
        if self.pos.y > HEIGHT + self.radius:
            self.kill()

    def update(self):
        # Spinning
        self.image = self.image_org.copy()
        self.rot += self.rot_speed
        self.image = pygame.transform.rotate(self.image, self.rot)
        self.rect = self.image.get_rect()
        self.hit_box = self.image_org.get_rect()

        self.pos += self.vel
        self.rect.center = self.pos
        self.hit_box.center = self.pos
        self.boundary()


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, state, pos, vel):
        pygame.sprite.Sprite.__init__(self)
        self.state = state
        self.image = pygame.image.load(POWER_UPS[self.state][0])
        self.rect = self.image.get_rect()
        self.radius = self.image.get_size()[0]
        self.pos = pos
        self.vel = vel
        self.rect.center = self.pos

    def boundary(self):
        # X axis
        if self.pos.x + self.radius < 0:
            self.kill()
        if self.pos.x > WIDTH + self.radius:
            self.kill()
        # Y axis
        if self.pos.y + self.radius < 0:
            self.kill()
        if self.pos.y > HEIGHT + self.radius:
            self.kill()

    def update(self):
        self.pos += self.vel
        self.rect.center = self.pos
        self.boundary()


# noinspection PyArgumentList
class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos, size='small', sonic=False, hit=False):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        if sonic:
            self.anim = [pygame.image.load(frame) for frame in SONIC]
            self.frame_rate = 100
        else:
            self.anim = [pygame.image.load(frame) for frame in EXPLOSION]
            self.frame_rate = 50
        if self.size == 'small':
            self.image = pygame.transform.scale(self.anim[0], (20, 20))
        if self.size == 'big':
            self.image = pygame.transform.scale(self.anim[0], (75, 75))
        if self.size == 'huge':
            self.image = pygame.transform.scale(self.anim[0], (130, 130))
        if hit:
            pygame.mixer.Sound(random.choice(HIT_SOUND)).play()
        if not hit:
            pygame.mixer.Sound(random.choice(EXPLOSION_SOUND)).play()
        self.frame = 1
        self.pos = vec(pos.x, pos.y)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.last_change = pygame.time.get_ticks()

    def update(self):
        # Change frame
        now = pygame.time.get_ticks()
        if now - self.last_change > self.frame_rate:
            self.last_change = now
            if self.frame == len(self.anim):
                self.kill()
            else:
                if self.size == 'small':
                    self.image = pygame.transform.scale(self.anim[self.frame], (20, 20))
                if self.size == 'big':
                    self.image = pygame.transform.scale(self.anim[self.frame], (75, 75))
                    self.rect = self.image.get_rect()
                if self.size == 'huge':
                    self.image = pygame.transform.scale(self.anim[self.frame], (130, 130))
                self.frame += 1
        self.rect.center = self.pos
