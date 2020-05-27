# Importing the libraries

from conf import *
from sprites import *
import os
import pygame
import random

# Centralize the window

os.environ['SDL_VIDEO_CENTERED'] = '1'

# Initialising pygame
pygame.init()
pygame.mixer.init()

# Loading files
background_image = pygame.image.load('gallery/sprites/background.png')


# noinspection PyArgumentList
class Game:
    def __init__(self):
        # self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption('Asteroids')
        self.running = True
        self.bg_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.asteroids = pygame.sprite.Group()
        self.meteors = pygame.sprite.Group()
        self.lasers = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.player = Player(self)
        self.players.add(self.player)
        self.last_spawn = pygame.time.get_ticks()
        self.high_score = 0
        self.difficulty = NUMBER
        self.waiting = False

    def run(self):
        pygame.mixer.music.load('gallery/audio/background_song.mp3')
        pygame.mixer.music.play(loops=-1)
        while self.running:
            self.clock.tick(30)
            self.events()
            self.update()
            self.draw()
        pygame.mixer.music.fadeout(1500)

    # noinspection PyMethodMayBeStatic
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit()

    def spawn(self, state, randomize=False):
        # Randomly choosing spawn point
        spawn_choice = [(WIDTH // 2, -100), (WIDTH // 2, HEIGHT + 100),
                        (-100, HEIGHT // 2), (100, HEIGHT // 2)]
        spawn = random.choice(spawn_choice)

        # Randomly choosing speed
        vel = vec(0, 0)
        while vel == vec(0, 0):
            if spawn == spawn_choice[0]:
                vel = vec(random.randrange(-10, 10), random.randrange(-10, 0))
            if spawn == spawn_choice[1]:
                vel = vec(random.randrange(-10, 10), random.randrange(0, 10))
            if spawn == spawn_choice[2]:
                vel = vec(random.randrange(-10, 0), random.randrange(-10, 10))
            if spawn == spawn_choice[3]:
                vel = vec(random.randrange(0, 10), random.randrange(-10, 10))
        if state == 'asteroid':
            if randomize:
                size = random.choice([BIG, MEDIUM, SMALL])
            else:
                size = BIG
            self.asteroids.add(Asteroid(self, size, spawn, vel))
        if state == 'meteor':
            size = random.choice([BIG0, MEDIUM0])
            self.meteors.add(Meteor(self, size, spawn, vel))

    def update(self):
        # Spawning the meteor
        chance = random.randrange(10000)
        if chance <= CHANCE:
            self.spawn('meteor')

        if len(self.asteroids) == 0:
            self.spawn('asteroid')
        now = pygame.time.get_ticks()
        if now - self.last_spawn > SPAWN_COOLDOWN and len(self.asteroids) < self.difficulty:
            self.spawn('asteroid')
            self.last_spawn = now

        # Laser collison with meteor
        for meteor in self.meteors:
            for laser in self.lasers:
                if laser.rect.colliderect(meteor.hit_box):
                    self.player.streak -= 1
                    laser.kill()
                    # Creating explosion
                    self.explosions.add(Explosion(meteor.pos))

        # Player collision with meteor
        if pygame.sprite.spritecollide(self.player, self.meteors, False, pygame.sprite.collide_circle):
            self.player.health = 0
            self.player.streak = 0

        for asteroid in self.asteroids:
            # Laser collsion with asteroid
            for laser in self.lasers:
                if laser.rect.colliderect(asteroid.hit_box):
                    if asteroid.size != SMALL:
                        self.explosions.add(Explosion(asteroid.pos, 'big'))
                    else:
                        self.explosions.add(Explosion(asteroid.pos))
                    asteroid.break_of()
                    laser.kill()
                    self.player.streak += 1
                    # Chance to spawn power up
                    state = random.choice([key for key in POWER_UPS.keys()])
                    chance = random.randrange(100)
                    if chance < POWER_UPS[state][1]:
                        self.power_ups.add(PowerUp(state, asteroid.pos, asteroid.vel))

            # Player collison with asteroid
            if pygame.sprite.spritecollide(asteroid, self.players, False, pygame.sprite.collide_circle):
                if asteroid.size == BIG:
                    self.player.health = 0
                else:
                    self.player.health -= asteroid.radius
                    self.explosions.add(Explosion(asteroid.pos, 'small', False, True))
                    asteroid.kill()
                self.player.streak = 0

        # Player gets a power up
        for powerup in self.power_ups:
            if pygame.sprite.spritecollide(powerup, self.players, False):
                pygame.mixer.Sound(random.choice(POWER_SOUND)).play()
                # Repair
                if powerup.state == 'repair':
                    powerup.kill()
                    self.player.health += random.randrange(20, REPAIR)
                # Refill
                if powerup.state == 'refill':
                    powerup.kill()
                    self.player.juice = 100

        if self.player.streak < 0:
            self.player.streak = 0

        # Check player health
        if self.player.health > 100:
            self.player.health = 100
        if self.player.health <= 0 and self.player.alive():
            self.player.kill()
            # Start huge explosion
            self.explosions.add(Explosion(self.player.pos, 'huge', True))

        # If player is dead and explosion has finished playing end game
        if not self.player.alive() and not len(self.explosions):
            self.running = False

        # Increase difficulty
        if self.player.score > 300:
            self.difficulty += 10
        if self.player.score > 500:
            self.difficulty += 10
        if self.player.score > 1000:
            self.difficulty += 10

        self.asteroids.update()
        self.explosions.update()
        self.meteors.update()
        self.lasers.update()
        self.players.update()
        self.power_ups.update()

    def draw_text(self, size, text, colour, x, y, rot=0):
        font = pygame.font.Font('gallery/Futured.TTF', size)
        text_surface = font.render(text, 1, colour)
        text_surface = pygame.transform.rotate(text_surface, rot)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def health_bar(self):
        outline = pygame.Rect(19, 45, 102, 20)
        pygame.draw.rect(self.screen, RED, outline, 2)
        inside = pygame.Rect(20, 47, self.player.health, 18)
        pygame.draw.rect(self.screen, GREEN, inside)

    def juice_bar(self):
        outline = pygame.Rect(19, 75, 102, 20)
        pygame.draw.rect(self.screen, RED, outline, 2)
        inside = pygame.Rect(20, 77, self.player.juice, 18)
        pygame.draw.rect(self.screen, BLUE, inside)

    def draw(self):
        self.screen.blit(self.bg_image, (0, 0))
        self.asteroids.draw(self.screen)
        self.meteors.draw(self.screen)
        self.lasers.draw(self.screen)
        self.players.draw(self.screen)
        self.power_ups.draw(self.screen)
        self.explosions.draw(self.screen)

        # for asteroid in self.asteroids:
        #     pygame.draw.circle(self.screen, RED, asteroid.rect.center, asteroid.radius, 2)
        # for meteor in self.meteors:
        #     pygame.draw.circle(self.screen, RED, meteor.rect.center, meteor.radius, 2)
        # # pygame.draw.circle(self.screen, GREEN, self.player.rect.center, self.player.radius, 2)

        # for asteroid in self.asteroids:
        #     pygame.draw.rect(self.screen, RED, asteroid.hit_box, 2)
        # for meteor in self.meteors:
        #     pygame.draw.rect(self.screen, RED, meteor.hit_box, 2)
        # pygame.draw.rect(self.screen, GREEN, self.player.rect, 2)

        self.draw_text(40, f'{self.player.score}', BLUE, WIDTH // 2, 30)
        self.draw_text(25, f'x {self.player.streak}', WHITE, WIDTH // 2 + 40, 25, -30)
        self.health_bar()
        self.juice_bar()
        pygame.display.flip()

    def check_highscore(self):
        try:
            with open('High Score', 'r') as score_file:
                self.high_score = int(score_file.read())
        except FileNotFoundError:
            self.high_score = 0

        if self.player.score > self.high_score:
            with open('High Score', 'w') as score_file:
                score_file.write(str(self.player.score))
            self.high_score = self.player.score
            return True
        else:
            return False

    def start_screen(self):
        pygame.mixer.music.load('gallery/audio/Game_Over.mp3')
        pygame.mixer.music.play(-1)
        self.check_highscore()
        self.waiting = True
        last_spawn = pygame.time.get_ticks()
        while self.waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        quit()
            mouse = pygame.mouse.get_pressed()
            if mouse[0]:
                self.waiting = False
            # Spawn
            now = pygame.time.get_ticks()
            if len(self.asteroids) < 10 and now - last_spawn > 1000:
                self.spawn('asteroid', True)
            if len(self.meteors) < 5 and now - last_spawn > 1000:
                self.spawn('meteor')
                last_spawn = now

            # Update
            self.asteroids.update()
            self.meteors.update()

            # Draw
            self.screen.blit(self.bg_image, (0, 0))
            self.asteroids.draw(self.screen)
            self.meteors.draw(self.screen)
            self.draw_text(20, f'{self.high_score}', BLUE, WIDTH // 2, HEIGHT // 2 + 90)
            self.draw_text(50, 'START', BLUE, WIDTH // 2, HEIGHT // 2)
            self.draw_text(40, 'HIGH SCORE', BLUE, WIDTH // 2, HEIGHT // 2 + 60)
            pygame.display.flip()
        for asteroid in self.asteroids:
            asteroid.kill()
        for meteor in self.meteors:
            meteor.kill()
        pygame.mixer.music.fadeout(500)

    def go_screen(self):
        pygame.mixer.music.load('gallery/audio/wait.mp3')
        pygame.mixer.music.play(-1)
        self.check_highscore()
        self.waiting = True
        while self.waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        quit()
            mouse = pygame.mouse.get_pressed()
            if mouse[0]:
                self.waiting = False

            # Update
            self.asteroids.update()
            self.meteors.update()

            # Draw
            self.screen.blit(self.bg_image, (0, 0))
            self.asteroids.draw(self.screen)
            self.meteors.draw(self.screen)
            self.draw_text(40, f'{self.player.score}', BLUE, WIDTH // 2, 30)
            self.draw_text(60, 'GAME OVER', BLUE, WIDTH // 2, HEIGHT // 2)
            self.draw_text(20, f'{self.high_score}', BLUE, WIDTH // 2, HEIGHT // 2 + 90)
            self.draw_text(40, 'HIGH SCORE', BLUE, WIDTH // 2, HEIGHT // 2 + 60)

            pygame.display.flip()
        for asteroid in self.asteroids:
            asteroid.kill()
        for meteor in self.meteors:
            meteor.kill()
        pygame.mixer.music.fadeout(500)


game = Game()
while True:
    game.start_screen()
    game.__init__()
    game.run()
    game.check_highscore()
    game.go_screen()
