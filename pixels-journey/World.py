import pygame
from Coin import Coin
from Enemy import Enemy
from Lava import Lava
from Exit import Exit

class World():
    def __init__(self, data, coin_group, lava_group, blob_group, exit_group, tile_size):
        self.tile_list = []

        # Dummy coin to make score look better
        score_coin = Coin(tile_size // 2, tile_size // 2 , tile_size)
        coin_group.add(score_coin)

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
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2), tile_size)
                    lava_group.add(lava)
                if tile == 5:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2), tile_size)
                    exit_group.add(exit)
                if tile == 6:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size - (tile_size // 2), tile_size)
                    coin_group.add(coin)
                col_count += 1
            row_count += 1
    def draw(self, screen):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            #pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)