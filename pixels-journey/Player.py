import controls
import pygame


class Player():
    def __init__(self, x, y, device):
       self.reset(x, y)
       self.device = device

       # Sounds used by Player
       self.jump_fx = pygame.mixer.Sound('img/jump.wav')
       self.jump_fx.set_volume(0.5)
       self.game_over_fx = pygame.mixer.Sound('img/game_over.wav')
       self.game_over_fx.set_volume(0.5)

    def update(self, game_over, world, blob_group, lava_group, exit_group, screen):
        dx = 0
        dy = 0
        walk_cooldown = 20

        if game_over == 0:
            control = controls.controller(self.device)

            # Movement
            if control["JUMP"] and self.jumped == False:
                self.jump_fx.play()
                self.jumped = True
                self.vel_y = -15
            if control["JUMP"] == False and self.in_air == False:
                self.jumped = False
            if control["LEFT"]:
                dx -= 5
                self.counter += 5
                self.direction = -1
            if control["RIGHT"]:
                dx += 5
                self.counter += 5
                self.direction = 1
            if control["LEFT"] == False and control["RIGHT"] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Walking animation
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Gravity
            self.vel_y += 1
            if self.vel_y > 15:
                self.vel_y = 15
            dy += self.vel_y

            # Check collision for ground / platforms
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
                self.game_over_fx.play()

            # check collision with lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                self.game_over_fx.play()

            # check collision with exit
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            #update player coordinates
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
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