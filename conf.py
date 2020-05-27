# General adjustments
# WIDTH = 800
# HEIGHT = 600
WIDTH = 1366
HEIGHT = 768

# Player setting
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 30
PLAYER_ACC = .7
FRICTION = -.01
LASER_SPEED = 50
COOL_DOWN = 200
COST = 5
INCREASE = .1
SPREAD = 5
LASER_JUMP = 10
KNOCK_BACK = -1
EXPLOSION = [f'gallery/sprites/regularExplosion0{num}.png' for num in range(9)]
SONIC = [f'gallery/sprites/sonicExplosion0{num}.png' for num in range(9)]
LASER_SOUND = [f'gallery/audio/Laser_Shoot{num}.wav' for num in range(5)]
EXPLOSION_SOUND = [f'gallery/audio/Explosion{num}.wav' for num in range(8)]
HIT_SOUND = [f'gallery/audio/Hit_Hurt{num}.wav' for num in range(6)]
POWER_SOUND = [f'gallery/audio/Powerup{num}.wav' for num in range(8)]

# Asteroid setting
BIG = [f'gallery/sprites/meteorBrown_big{num}.png' for num in range(1, 5)]
MEDIUM = [f'gallery/sprites/meteorBrown_med{num}.png' for num in range(1, 3)]
SMALL = [f'gallery/sprites/meteorBrown_small{num}.png' for num in range(1, 5)]
NUMBER = 20
DISPERSE = 15
SPAWN_COOLDOWN = 5000
ROT_SPEED = 7

# Meteor setting
BIG0 = [f'gallery/sprites/meteorGrey_big{num}.png' for num in range(1, 5)]
MEDIUM0 = [f'gallery/sprites/meteorGrey_med{num}.png' for num in range(1, 3)]
CHANCE = 150  # out of 10000

# Power up
POWER_UPS = {'repair': ['gallery/sprites/repair_powerup.png', 30],
             'refill': ['gallery/sprites/refill.png', 30]}
REPAIR = 30

# Colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
