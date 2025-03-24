import pickle
import pygame
from pygame import mixer
import controls
from os import path
from World import World
from Player import Player
from Button import Button
import math
import time

class Game:
    def __init__(self):
        # Initialization
        pygame.mixer.pre_init(44100, -16, 2, 512)
        mixer.init()
        pygame.init()
        self.device = controls.select_controller()

        # Colors
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)

        # Screen size
        self.screen_width = 1000
        self.screen_height = 1000
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        #pygame.display.set_caption("Pixel's Journey")

        # Fonts
        self.font = pygame.font.SysFont('Courier New', 70)
        self.font_score = pygame.font.SysFont('Courier New', 30) 

        self.FPS = 60

        self.clock = pygame.time.Clock()

        # Game variables
        self.tile_size = 50
        self.game_over = 0
        self.main_menu = True
        self.level = 1
        self.difficulty = 1 # default to easy
        self.difficulty_selected = False
        self.max_levels = 3
        self.score = 0

        # Images
        self.bg_img = pygame.transform.scale(pygame.image.load('img/sky.png'), (self.screen_width, self.screen_height))
        self.restart_img = pygame.image.load('img/restart_btn.png')
        self.start_img = pygame.image.load('img/start_btn.png')
        self.menu_img = pygame.image.load('img/menu_btn.png')
        self.menu_img_small = pygame.image.load('img/menu_btn_small.png')
        self.difficulty_assets = {
            "easy": pygame.image.load('img/difficulty_easy.png'),
            "normal" : pygame.image.load('img/difficulty_normal.png'),
            "hard": pygame.image.load('img/difficulty_hard.png')
        }
        self.exit_img = pygame.image.load('img/exit_btn.png')

        # Sounds
        self.coin_fx = pygame.mixer.Sound('img/coin.wav')
        self.coin_fx.set_volume(0.5)

        pygame.mixer.music.load('img/music.wav')
        pygame.mixer.music.play(-1, 0.0, 10000)

        #buttons
        self.restart_button = Button(self.screen_width // 2 - 60, self.screen_height // 2 + 140, self.restart_img, self.screen)
        self.start_button = Button(self.screen_width // 2 - 139.5, self.screen_height // 2 - 150, self.start_img, self.screen)
        self.exit_button = Button(self.screen_width // 2 - 120, self.screen_height // 2 + 150, self.exit_img, self.screen)
        self.menu_button = Button(self.screen_width // 2 - 120, self.screen_height // 2, self.menu_img, self.screen)
        self.menu_button_small = Button(self.screen_width // 2 - 60, self.screen_height // 2 + 40, self.menu_img_small, self.screen)
        self.difficulty_buttons = {
            "easy": Button(self.screen_width // 2 - 60, self.screen_height // 2 - 140, self.difficulty_assets["easy"], self.screen),
            "normal": Button(self.screen_width // 2 - 60, self.screen_height // 2 - 70, self.difficulty_assets["normal"], self.screen),
            "hard": Button(self.screen_width // 2 - 60, self.screen_height // 2, self.difficulty_assets["hard"], self.screen)
        }

        # Sprite groups
        self.blob_group = pygame.sprite.Group()
        self.lava_group = pygame.sprite.Group()
        self.exit_group = pygame.sprite.Group()
        self.coin_group = pygame.sprite.Group()

        self.on_init()

    def on_init(self):
        self.player = Player(100, self.screen_height - 130, self.device)
        #load in level data and create world
        if path.exists(f'./levels/level{self.level}'):
            pickle_in = open(f'./levels/level{self.level}','rb')
            self.world_data = pickle.load(pickle_in)
        self.world = World(self.world_data, self.coin_group, self.lava_group, self.blob_group, self.exit_group, self.tile_size)

    def draw_text(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))

    def reset_level(self, level):
        self.player.reset(100, self.screen_height - 130)
        self.blob_group.empty()
        self.lava_group.empty()
        self.exit_group.empty()
        self.coin_group.empty()

        if path.exists(f'./levels/level{level}'):
            pickle_in = open(f'./levels/level{level}', 'rb')
            world_data = pickle.load(pickle_in)
        world = World(world_data, self.coin_group, self.lava_group, self.blob_group, self.exit_group, self.tile_size)

        return world

    def draw_grid(self):
        for line in range (0, 20):
            pygame.draw.line(self.screen, (255, 255, 255), (0, line * self.tile_size), (self.screen_width, line * self.tile_size))
            pygame.draw.line(self.screen, (255, 255, 255), (line * self.tile_size, 0), (line * self.tile_size, self.screen_height))

    def run(self):
        self.Run = True
        while self.Run:
            self.clock.tick(self.FPS)

            self.screen.blit(self.bg_img, (0, 0))

            if self.main_menu == True:
                if self.exit_button.draw():
                    self.Run = False
                if self.start_button.draw():
                    self.difficulty_selected = True
                    self.main_menu = False
                if self.menu_button.draw():
                    self.main_menu = False
                    self.difficulty_selected = False

            elif self.main_menu == False and self.difficulty_selected == False:
                self.device = controls.select_controller()
                if self.difficulty_buttons["easy"].draw():
                    self.difficulty = 1
                    self.difficulty_selected = True
                    self.main_menu = True
                    self.max_levels = 3
                    time.sleep(0.1)
                if self.difficulty_buttons["normal"].draw():
                    self.difficulty = 2
                    self.difficulty_selected = True
                    self.main_menu = True
                    self.max_levels = 4
                    time.sleep(0.1)
                if self.difficulty_buttons["hard"].draw():
                    self.difficulty = 3
                    self.difficulty_selected = True
                    self.main_menu = True
                    self.max_levels = 5
                    time.sleep(0.1)
                if self.device == "keyboard":
                    self.text = 'Arduino status: Disconnected'
                    self.text_width = self.font_score.size(self.text)[0]
                if self.device == "arduino":
                    self.text = 'Arduino status: Connected'
                    self.text_width = self.font_score.size(self.text)[0]
                self.draw_text(self.text, self.font_score, self.black, ((self.screen_width - self.text_width) // 2), self.screen_height // 2 + 70)
            else:
                self.world.draw(self.screen)

                if self.game_over == 0:
                    
                    
                    for i in range(self.difficulty):
                        self.blob_group.update()
                    #update score
                    if pygame.sprite.spritecollide(self.player, self.coin_group, True):
                        self.score += 1
                        self.coin_fx.play()
                    self.draw_text('X' + str(self.score), self.font_score, self.white, self.tile_size - 10, 10)
                    

                self.blob_group.draw(self.screen)
                self.lava_group.draw(self.screen)
                self.exit_group.draw(self.screen)
                self.coin_group.draw(self.screen)

                self.game_over = self.player.update(self.game_over, self.world, self.blob_group, self.lava_group, self.exit_group, self.screen)

                #if player dies display restart button
                if self.game_over == -1:
                    self.draw_text('GAME OVER!', self.font, self.black, (self.screen_width // 2) - 200, (self.screen_height // 2) - 200)
                    if self.restart_button.draw():
                        self.world_data = []
                        self.level = 1
                        self.world = self.reset_level(self.level)
                        self.game_over = 0
                        self.score = 0
                    if self.menu_button_small.draw():
                            self.level = 1
                            self.world_data = []
                            self.world = self.reset_level(self.level)
                            self.game_over = 0
                            self.score = 0
                            self.main_menu = True
                            self.difficulty_selected = False
                            time.sleep(0.1)

                #level completed go to the next
                if self.game_over == 1:
                    self.level += 1
                    if self.level <= self.max_levels:
                        self.world_data = []
                        self.world = self.reset_level(self.level)
                        self.game_over = 0
                    else:
                        self.draw_text('YOU WIN!', self.font, self.black, (self.screen_width // 2) - 160, (self.screen_height // 2) - 300)
                        if self.restart_button.draw():
                            self.level = 1
                            self.world_data = []
                            self.world = self.reset_level(self.level)
                            self.game_over = 0
                            self.score = 0
                        if self.menu_button_small.draw():
                            self.level = 1
                            self.world_data = []
                            self.world = self.reset_level(self.level)
                            self.game_over = 0
                            self.score = 0
                            self.main_menu = True
                            self.difficulty_selected = False
                            time.sleep(0.1)


                #draw_grid()


            for self.event in pygame.event.get():
                if self.event.type == pygame.QUIT:
                    self.Run = False

            pygame.display.update()
            pygame.display.set_caption(f"FPS: {math.floor(self.clock.get_fps())}")

        pygame.quit()