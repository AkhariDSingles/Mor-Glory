import pygame
from pygame.locals import *
from pygame import mixer

import pickle
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 750

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Mor Glory')

font_score = pygame.font.SysFont('chicago', 30)
font = pygame.font.SysFont('chicago', 70)

tile_size = 50
game_over = 0
main_menu = True
level = 1
score = 0
max_levels = 2



white = (255, 255, 255)
red = (230, 90, 150)



back_img = pygame.image.load('mor assets/parallax-mountain-bg.png')
back_img = pygame.transform.scale(back_img, (1000, 750))
bg3 = pygame.image.load('mor assets/parallax-mountain-montain-far.png')
bg3 = pygame.transform.scale(bg3, (500, 500))
bg4 = pygame.image.load('mor assets/parallax-mountain-mountains.png')
bg4 = pygame.transform.scale(bg4, (1000, 650))
bgtrees = pygame.image.load('mor assets/parallax-mountain-foreground-trees.png')
bgtrees = pygame.transform.scale(bgtrees, (1000, 750))
bg5 = pygame.image.load('mor assets/parallax-mountain-trees.png')
bg5 = pygame.transform.scale(bg5, (1000, 757))
restart_img = pygame.image.load('mor assets/restart.png')
restart_img = pygame.transform.scale(restart_img, (100, 100))
start_img = pygame.image.load('mor assets/start.png')
start_img = pygame.transform.scale(start_img, (250, 250))
exit_img = pygame.image.load('mor assets/exit.png')
exit_img = pygame.transform.scale(exit_img, (90, 90))



coin_fx = pygame.mixer.Sound('mor assets/coin.mp3')
coin_fx.set_volume(0.5)
death_fx = pygame.mixer.Sound('mor assets/dead.mp3')


pygame.mixer.music.load('mor assets/Mor Glory soundtrack/METHODICAL.wav')
pygame.mixer.music.play(-1, 0.0, 5000)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def reset_level(level):
    player.reset(60, screen_height - 60)
    bloop_group.empty()
    lava_group.empty()
    exit_group.empty()

    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        draw_text('MOR GLORY', font, red, (screen_width // 2) - 140, screen_height // 2)

        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False


        screen.blit(self.image, self.rect)

        return action


class Player:
    def __init__(self, x, y):
        self.reset(x, y)


    def update(self, game_over):

        dx = 0
        dy = 0
        walk_cooldown = 2
        if game_over == 0:
            # get keypresses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]



            if self.counter > walk_cooldown:
                 self.counter = 0
                 self.index += 1
                 if self.index >= len(self.images_right):
                     self.index = 0
                 if self.direction == 1:
                     self.image = self.images_right[self.index]
                 if self.direction == -1:
                     self.image = self.images_left[self.index]



            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y


            self.in_air = True
            for tile in world.tile_list:

                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0

                    elif self.vel_y >= 0:
                       dy = tile[1].top - self.rect.bottom
                       self.vel_y = 0
                       self.in_air = False

            if pygame.sprite.spritecollide(self, bloop_group, False):
               game_over = -1
               death_fx.play()
            if pygame.sprite.spritecollide(self, lava_group, False):
               game_over = -1
               death_fx.play()


               # check for collision with exit
            if pygame.sprite.spritecollide(self, exit_group, False):
                   game_over = 1

            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
            if self.rect.y > -1:
                self.rect.y -= 2

        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)


        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []

        self.index = 0
        self.counter = 0
        for i in range(6, 17):
            img_right = pygame.image.load(f'mor assets/tile{i}.png')
            img_right = pygame.transform.scale(img_right, (35, 60))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        for i in range(44, 49):
            self.dead_image = pygame.image.load(f'mor assets/tile{i}.png')
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

        dirt_img = pygame.image.load('mor assets/Remove background-2.png')
        grass_img = pygame.image.load('mor assets/2.jpg')

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
                    bloop = Enemy(col_count * tile_size, row_count * tile_size + 20)
                    bloop_group.add(bloop)
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                if tile == 7:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)


                col_count += 1
            row_count += 1


    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)



class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('mor assets/opps/tile010.png')
        self.image = pygame.transform.scale(self.image, (30, 30))
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
        img = pygame.image.load('mor assets/opps/lava1.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('mor assets/coins/coin.png')
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('mor assets/exitd.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

player = Player(60, screen_height - 60)
bloop_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)


restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)
run = True
while run:

    clock.tick(fps)
    screen.blit(back_img, (0, 0))
    screen.blit(bg3, (0, 0))
    screen.blit(bg4, (0, 10))
    screen.blit(bg5, (0, 0))
    screen.blit(bgtrees, (0, 0))

    if main_menu == True:
       if exit_button.draw():
           run = False
       if start_button.draw():
           main_menu = False

    else:
        world.draw()



        if game_over == 0:
            bloop_group.update()

            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
                coin_fx.play()
            draw_text('X' + str(score), font_score, white, tile_size - 10, 10)


        bloop_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)

        game_over = player.update(game_over)

        if game_over == -1:
            if restart_button.draw():
                 world_data = []
                 world = reset_level(level)
                 game_over = 0
                 score = 0

        if game_over == 1:
            level += 1
            if level <= max_levels:
               world_data = []
               world = reset_level(level)
               game_over = 0

            else:
                draw_text('MOR GLORY!', font, red, (screen_width // 2) - 140, screen_height // 2)
                if restart_button.draw():
                    level = 1
                    world_data = []
                    world = reset_level(level)
                    game_over = 0





    for event in pygame.event.get():
        if event.type == pygame.QUIT:
           run = False

    pygame.display.update()

pygame.quit()
