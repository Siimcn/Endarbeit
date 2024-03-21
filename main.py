import pygame
import sys
import os
import random
from settings import *
from scripts.utils import load_images, load_image, Animation
from scripts.entities import Player, Enemy
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds


class Game:
    def __init__(self):
        # screen / setup
        pygame.init()                                                   # initialisation
        self.screen = pygame.display.set_mode(RES)                      # setup window
        self.display = pygame.Surface(RESIZED_RES, pygame.SRCALPHA)     # surface to scale images
        self.display_2 = pygame.Surface(RESIZED_RES)
        self.clock = pygame.time.Clock()                                # setup a Clock object

        # fonts
        self.title_font_1 = pygame.font.Font("data/fonts/Pixeboy.ttf", 50)
        self.title_font_2 = pygame.font.Font("data/fonts/Pixeboy.ttf", 15)
        self.title_font_3 = pygame.font.Font("data/fonts/Pixeboy.ttf", 35)

        # rendered fonts
        self.title1 = self.title_font_1.render(f"ENDARBEIT", False, (255, 255, 255))
        self.title2 = self.title_font_1.render(f"SIMON RINGS", False, (255, 255, 255))
        self.title3 = self.title_font_2.render(f"press c to dash", False, (255, 255, 255))
        self.title4 = self.title_font_2.render(f"press x to attack", False, (255, 255, 255))
        self.end1 = self.title_font_3.render(f"THANK YOU FOR PLAYING!", False, (255, 255, 255))
        self.end2 = self.title_font_2.render(f"TUTOR: MORITZ SCHMITZ", False, (255, 255, 255))
        self.end3 = self.title_font_2.render(f"ABITURIENT: SIMON RINGS", False, (255, 255, 255))
        self.end4 = self.title_font_3.render(f"SEE YOU NEXT TIME!", False, (255, 255, 255))

        # assets
        self.assets = {
            "background_sky": load_image("background_sky.png"),
            "background_desert": load_image("background_desert.png"),
            "background_dungeon": pygame.image.load("data/images/background_dungeon.png").convert(),
            "background_night": load_image("background_night.png"),
            "background_end": load_image("background_end.png"),
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "grass_2": load_images("tiles/grass_2"),
            "stone": load_images("tiles/stone"),
            "sand_normal": load_images("tiles/sand_normal"),
            "sand_orange": load_images("tiles/sand_orange"),
            "large_decor": load_images("tiles/large_decor"),
            "clouds": load_images("clouds"),
            "clouds_desert": load_images("clouds_desert"),
            "clouds_night": load_images("clouds_night"),
            "slime/idle": Animation(load_images("entities/slime/idle"), image_duration=10),
            "slime/run": Animation(load_images("entities/slime/run"), image_duration=8),
            "skeleton/idle": Animation(load_images("entities/skeleton/idle"), image_duration=10),
            "skeleton/run": Animation(load_images("entities/skeleton/run"), image_duration=8),
            "ghost/idle": Animation(load_images("entities/ghost/idle"), image_duration=10),
            "ghost/run": Animation(load_images("entities/ghost/run"), image_duration=8),
            "player/idle": Animation(load_images("entities/player/idle"), image_duration=8),
            "player/run": Animation(load_images("entities/player/run"), image_duration=6),
            "player/jump": Animation(load_images("entities/player/jump")),
            "player/attack": Animation(load_images("entities/player/attack"), image_duration=4, loop=False),
            "particle/particle": Animation(load_images("particles/particle"), image_duration=20, loop=False),

        }

        # sounds / sound effects
        self.sfx = {
            "ambience": pygame.mixer.Sound("data/sfx/ambience.wav"),
            "dash": pygame.mixer.Sound("data/sfx/dash.wav"),
            "hit": pygame.mixer.Sound("data/sfx/hit.wav"),
            "jump": pygame.mixer.Sound("data/sfx/jump.wav"),
            "attack": pygame.mixer.Sound("data/sfx/attack.wav"),
        }

        # adjust sounds volume
        self.sfx["ambience"].set_volume(0.2)
        self.sfx["dash"].set_volume(1)
        self.sfx["hit"].set_volume(0.8)
        self.sfx["jump"].set_volume(0.3)
        self.sfx["attack"].set_volume(1)

        # clouds
        self.clouds = Clouds(self.assets["clouds"], count=16)
        self.clouds_desert = Clouds(self.assets["clouds_desert"], count=6)
        self.clouds_night = Clouds(self.assets["clouds_night"], count=16)

        # entities
        self.movement = [False, False]
        self.player = Player(self, (50, 50), (13, 15))

        # particles
        self.particles = []

        # tiles
        self.tilemap = Tilemap(self, tile_size=16)
        # self.tilemap.load('map.json')

        # camera
        self.scroll = [0, 0]
        self.render_scroll = (0, 0)

        # level
        self.level = 0
        self.load_level(self.level)

        self.screenshake = 1

    def title_font(self, offset=(0, 0)):
        title1_rect = self.title1.get_rect(topleft=(100 - offset[0], -100 - offset[1]))
        title2_rect = self.title2.get_rect(topleft=(85 - offset[0], -70 - offset[1]))
        title3_rect = self.title3.get_rect(topleft=(163 - offset[0], -30 - offset[1]))
        title4_rect = self.title4.get_rect(topleft=(157 - offset[0], -40 - offset[1]))
        self.display_2.blit(self.title1, title1_rect)
        self.display_2.blit(self.title2, title2_rect)
        self.display_2.blit(self.title3, title3_rect)
        self.display_2.blit(self.title4, title4_rect)

    def end_font(self, offset=(0, 0)):
        end1_rect = self.end1.get_rect(topleft=(140 - offset[0], -100 - offset[1]))
        end2_rect = self.end2.get_rect(topleft=(152 - offset[0], -70 - offset[1]))
        end3_rect = self.end3.get_rect(topleft=(292 - offset[0], -70 - offset[1]))
        end4_rect = self.end4.get_rect(topleft=(292 - offset[0], 400 - offset[1]))
        self.display_2.blit(self.end1, end1_rect)
        self.display_2.blit(self.end2, end2_rect)
        self.display_2.blit(self.end3, end3_rect)
        self.display_2.blit(self.end4, end4_rect)

    def load_level(self, map_id):
        self.tilemap.load("data/maps/" + str(map_id) + ".json")

        # music
        if map_id == 0:
            pygame.mixer.music.load("data/start.aif")
            pygame.mixer.music.set_volume(0.6)
        elif map_id == 1:
            pygame.mixer.music.load("data/desert.aif")
            pygame.mixer.music.set_volume(0.3)
        elif map_id == 2:
            pygame.mixer.music.load("data/dungeon.aif")
            pygame.mixer.music.set_volume(0.6)
        elif map_id == 3:
            pygame.mixer.music.load("data/night.aif")
            pygame.mixer.music.set_volume(0.6)
        elif map_id == 4:
            pygame.mixer.music.load("data/end.aif")
            pygame.mixer.music.set_volume(0.6)
        else:
            pygame.mixer.music.load("data/start.aif")
            pygame.mixer.music.set_volume(0.6)

        pygame.mixer.music.play(-1)
        self.sfx["ambience"].stop()

        if map_id == 0 or map_id == 3 or map_id == 4:
            self.sfx["ambience"].play(-1)

        # spawner
        self.enemies = []
        for spawner in self.tilemap.extract([("spawners", 0), ("spawners", 1), ("spawners", 2), ("spawners", 3)]):
            if spawner["variant"] == 0:
                self.player.pos = spawner["pos"]
                self.player.air_time = 0
            elif spawner["variant"] == 1:
                self.enemies.append(Enemy(self, "slime", spawner["pos"], (16, 6)))
            elif spawner["variant"] == 2:
                self.enemies.append(Enemy(self, "skeleton", spawner["pos"], (11, 11)))
            elif spawner["variant"] == 3:
                self.enemies.append(Enemy(self, "ghost", spawner["pos"], (11, 11)))

        self.projectiles = []
        self.particles = []
        self.sparks = []

        self.scroll = [0, 0]
        self.dead = -1
        self.transition = -30
        self.player.dashes = 3

    def draw(self):
        # screenshake
        self.screenshake = max(0, self.screenshake - 1)

        if not len(self.enemies):
            self.transition += 1
            if self.transition > 30:
                self.level = min(self.level + 1, len(os.listdir("data/maps/")) - 1)
                self.load_level(self.level)
        if self.transition < 0:
            self.transition += 1

        if self.dead:
            self.dead += 1
            if self.dead == 10:
                self.transition = min(30, self.transition + 1)
            if self.dead >= 40:
                self.load_level(self.level)

        # screen
        self.display.fill((0, 0, 0, 0))
        # background
        if self.level == 0:
            self.display_2.blit(self.assets["background_sky"], (0, 0))
        if self.level == 1:
            self.display_2.blit(self.assets["background_desert"], (0, 0))
        if self.level == 2:
            self.display_2.blit(self.assets["background_dungeon"], (0, 0))
        if self.level == 3:
            self.display_2.blit(self.assets["background_night"], (0, 0))
        if self.level == 4:
            self.display_2.blit(self.assets["background_end"], (0, 0))
        # clouds
        if self.level == 0:
            self.clouds.render(self.display, offset=self.render_scroll)
        if self.level == 1 or self.level == 4:
            self.clouds_desert.render(self.display, offset=self.render_scroll)
        if self.level == 3:
            self.clouds_night.render(self.display, offset=self.render_scroll)
        # tilemap
        self.tilemap.render(self.display, offset=self.render_scroll)
        # font
        if self.level == 0:
            self.title_font(offset=self.render_scroll)
        if self.level == 4:
            self.end_font(offset=self.render_scroll)
        # enemy
        for enemy in self.enemies.copy():
            kill = enemy.update(self.tilemap, (0, 0))
            enemy.render(self.display, offset=self.render_scroll)
            if kill:
                self.enemies.remove(enemy)
        # player
        self.player.render(self.display, offset=self.render_scroll)
        # outline
        display_mask = pygame.mask.from_surface(self.display)
        display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
        for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            self.display_2.blit(display_sillhouette, offset)
        # particles
        for particle in self.particles.copy():
            kill = particle.update()
            particle.render(self.display, offset=self.render_scroll)
            if kill:
                self.particles.remove(particle)
        # transition
        if self.transition:
            transition_surf = pygame.Surface(self.display.get_size())
            pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8)
            transition_surf.set_colorkey((255, 255, 255))
            self.display.blit(transition_surf, (0, 0))
        # rendered stuff
        self.display_2.blit(self.display, (0, 0))
        # screenshake
        screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
        # resized surface
        self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)

    def update(self):
        # clouds
        self.clouds.update()
        self.clouds_desert.update()
        self.clouds_night.update()
        # player
        self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
        # camera
        self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
        self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
        self.render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
        # window and FPS
        pygame.display.flip()                                           # updates screen
        self.clock.tick(FPS)                                            # set FPS
        pygame.display.set_caption(f"{self.clock.get_fps() : .2f}")     # see how much fps you have in caption top right

    def check_events(self):
        for event in pygame.event.get():                                # get events
            if event.type == pygame.QUIT:                               # when clicking on exit window
                pygame.quit()                                           # uninitializes all pygame modules
                sys.exit()                                              # terminates the Python program immediately
            if event.type == pygame.KEYDOWN:                            # event when pressing the key
                if event.key == pygame.K_a:
                    self.movement[0] = True
                if event.key == pygame.K_d:
                    self.movement[1] = True
                if event.key == pygame.K_w:
                    if self.player.jump():
                        self.sfx["jump"].play()
                if event.key == pygame.K_x:
                    if self.player.attack_active <= 0:
                        self.player.attack()
                if event.key == pygame.K_c:
                    self.player.dash()
                # if event.key == pygame.K_o:                           # skip level
                #     self.enemies = []
            if event.type == pygame.KEYUP:                              # event when letting go of the key
                if event.key == pygame.K_a:
                    self.movement[0] = False
                if event.key == pygame.K_d:
                    self.movement[1] = False

    def run(self):
        while True:                                                     # game loop
            self.draw()
            self.check_events()
            self.update()


# run game
if __name__ == "__main__":
    """
    statement ensures that the code block beneath it executes only
    when the Python script is run directly, not when it's imported 
    as a module.
    """
    game = Game()
    game.run()
