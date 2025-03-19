import pygame
from pygame import mixer
import pickle
from os import path, listdir
from time import time

#game variables
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pixel's Journey")

font = pygame.font.SysFont('Courier New', 70)
font_score = pygame.font.SysFont('Courier New', 30)
white = (255, 255, 255)

tile_size = 50
game_over = 0
main_menu = True
level = 1
difficulty = 1 # default to easy
difficulty_selected = False

# counting existing level pickles
max_levels = 3

score = 0

#images
bg_img = pygame.transform.scale(pygame.image.load('img/sky.png'), (screen_width, screen_height))
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
difficulty_assets = {
    "easy": pygame.image.load('img/difficulty_easy.png'),
    "normal" : pygame.image.load('img/difficulty_normal.png'),
    "hard": pygame.image.load('img/difficulty_hard.png')
}
exit_img = pygame.image.load('img/exit_btn.png')

#sounds
coin_fx = pygame.mixer.Sound('img/coin.wav')
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('img/jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('img/game_over.wav')
game_over_fx.set_volume(0.5)

pygame.mixer.music.load('img/music.wav')
pygame.mixer.music.play(-1, 0.0, 10000)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def reset_level(level):
    player.reset(100, screen_height - 130)
    blob_group.empty()
    lava_group.empty()
    exit_group.empty()
    coin_group.empty()

    if path.exists(f'./levels/level{level}'):
        pickle_in = open(f'./levels/level{level}', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world

def draw_grid():
    for line in range (0, 20):
        pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
        pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect =self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        #mouse position
        pos = pygame.mouse.get_pos()

        #if button is clicked
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, self.rect)

        return action


class Player():
    def __init__(self, x, y):
       self.reset(x, y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 20

        if game_over == 0:
            #get key presses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False:
                jump_fx.play()
                self.jumped = True
                self.vel_y = -15
            if key[pygame.K_SPACE] == False and self.in_air == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 5
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 5
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            #animation
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            #gravity
            self.vel_y += 1
            if self.vel_y > 15:
                self.vel_y = 15
            dy += self.vel_y

            #check collision for ground / platforms
            self.in_air = True
            for tile in world.tile_list:
                #y
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #checking if hitting above or below
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

                #x
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

            #check collision for enemies
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
                game_over_fx.play()

            # check collision with lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_fx.play()

            # check collision with exit
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            #update player coordinates
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
            draw_text('GAME OVER!', font, white, (screen_width // 2) - 200, screen_height // 2)
            if self.rect.y > -50:
                self.rect.y -= 5

        #draw player
        screen.blit(self.image, self.rect)
        #pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f'img/guy{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('img/ghost.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True


class World():
    def __init__(self, data):
        self.tile_list = []

        #load images
        dirt_img = pygame.image.load('img/dirt.png')
        grass_img = pygame.image.load('img/grass.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    blob_group.add(blob)
                if tile == 4:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                if tile == 5:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                if tile == 6:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size - (tile_size // 2))
                    coin_group.add(coin)
                col_count += 1
            row_count += 1
    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            #pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/blob.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/exit.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size * 1.5))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/coin.png')
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

player = Player(100, screen_height - 130)

blob_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()

#load in level data and create world
if path.exists(f'./levels/level{level}'):
    pickle_in = open(f'./levels/level{level}','rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)

#buttons
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)
difficulty_buttons = {
    "easy": Button(screen_width // 2 - 50, screen_height // 2 + 30, difficulty_assets["easy"]),
    "normal": Button(screen_width // 2 - 50, screen_height // 2 + 70, difficulty_assets["normal"]),
    "hard": Button(screen_width // 2 - 50, screen_height // 2 + 110, difficulty_assets["hard"])
}

run = True
while run:
    start_fps = time()
    clock.tick(fps)

    screen.blit(bg_img, (0, 0))

    if main_menu == True:
        if exit_button.draw():
            run = False
        if start_button.draw():
            screen.blit(bg_img, (0, 0))
            main_menu = False

    elif main_menu == False and difficulty_selected == False:
        if difficulty_buttons["easy"].draw():
            difficulty = 1
            difficulty_selected = True
            max_levels = 3
        if difficulty_buttons["normal"].draw():
            difficulty = 3
            difficulty_selected = True
            max_levels = 4
        if difficulty_buttons["hard"].draw():
            difficulty = 5
            difficulty_selected = True
            max_levels = 5
    else:
        world.draw()

        if game_over == 0:
            
            
            for i in range(0, difficulty):
                blob_group.update()
            #update score
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
                coin_fx.play()
            draw_text('X' + str(score), font_score, white, tile_size - 10, 10)
            # Dummy coin to make score look better
            score_coin = Coin(tile_size // 2, tile_size // 2)
            coin_group.add(score_coin)

        blob_group.draw(screen)
        lava_group.draw(screen)
        exit_group.draw(screen)
        coin_group.draw(screen)

        game_over = player.update(game_over)

        #if player dies display restart button
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                level = 1
                world = reset_level(level)
                game_over = 0
                score = 0
                # Dummy coin to make score look better
                score_coin = Coin(tile_size // 2, tile_size // 2)
                coin_group.add(score_coin)

        #level completed go to the next
        if game_over == 1:
            level += 1
            if level <= max_levels:
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                draw_text('YOU WIN!', font, white, (screen_width // 2) - 140, screen_height // 2)
                if restart_button.draw():
                    level = 1
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0


        #draw_grid()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()
    print(f"FPS: { 1 / (time() - start_fps):2f}")

pygame.quit()