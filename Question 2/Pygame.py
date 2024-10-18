#Group name:[Cas group 305]
#Group Members:
#[Reece Colgan] - S377586
#[Hayden Powell] - S376682
#[Daniel Sales] - S322244
#[Luke Few] - S348831
# Group 305 - Side Scrolling Pygame

#we used the tutorial by Coding with Russ (https://www.youtube.com/playlist?list=PLjcN1EyupaQm20hlUE11y9y8EY2aXLpnv) 
#and modified the code where necessary to make this game
#if you look at the history of the game on github you can see that we have been working
#on this bit by bit for the last few weeks few weeks


import os
import math
import random
import csv
import button


# try to open pygame
try:
    import pygame
except ImportError:  # if pygame is not installed, install it then open it
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
    import pygame
    
from pygame import mixer

mixer.init()
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Game')

clock = pygame.time.Clock()
FPS = 45
ROWS = 16
COLS = 150
TILE_TYPES = 21

#define game variables
GRAVITY = 0.65
MAX_LEVELS = 3
SCROLL_THRESH = 300
screen_scroll = 0
bg_scroll = 0
TILE_SIZE = SCREEN_HEIGHT //ROWS
level = 1
start_game = False
boss_counter = 0
points = 0
lives = 3

#define player action variables
left = False
right = False
shoot = False
grenade = False
grenade_thrown = False

pygame.mixer.music.load('audio/music2.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 4000)
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.5)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.5)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.5)

#load images
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
#background
pine1_img = pygame.image.load('img/background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/background/mountain.png').convert_alpha()
sky_cloud_img = pygame.image.load('img/background/sky_cloud.png').convert_alpha()
#tiles
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/Tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
#bullet
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
#grenade
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
#pick up boxes
health_box_image = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_image = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_image = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
item_boxes = {
    'Health' : health_box_image,
    'Ammo' : ammo_box_image,
    'Grenade' : grenade_box_image
    }

BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255 )
BLACK = (0, 0, 0)
GOLD = (255, 185, 15)

font = pygame.font.SysFont('Futura', 30)
big_font = pygame.font.SysFont('Futura', 60)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y)) 

def draw_bg():
    screen.fill(BG)
    width = sky_cloud_img.get_width()
    for x in range (5):
        screen.blit(sky_cloud_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))

def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    #create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = 100
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.jump_cooldown = 0
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        #ai variables
        self.move_counter=0
        self.vision = pygame.Rect(0,0,TILE_SIZE*3, 20)
        self.idling=False
        self.idling_counter=0
        self.ai_patrol_length = 30
        self.idle_length = 200
        #boss variables
        if level == 3 and char_type == 'enemy':
            scale = 1
            self.speed = 7
            self.vision = pygame.Rect(0,0,TILE_SIZE*1, 50)
            self.ammo=0
            self.ai_patrol_length = 260//self.speed  
            self.idle_length = 50
            self.health = 500
            self.max_health = self.health
        if level == 3 and char_type == 'player':
            self.ammo=0
            self.grenades=0

        #load all images
        animation_types = ['idle', 'run', 'jump', 'death']
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.jump_cooldown >0:
            self.jump_cooldown -=1

    def move(self, left, right):
        #reset movement at the start of each frame (otherwise character would move constantly until the direction was changed)
        screen_scroll = 0
        dx = 0
        dy = 0

        if left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        #jump
        if self.jump and not self.in_air and self.jump_cooldown == 0 and self.alive:
            self.vel_y = -15
            self.jump = False
            self.in_air = True
            
        #jump cooldown, needed to stop player from jumping before touching ground
        if self.in_air:
            self.jump_cooldown = 4
            
        #apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 15:
            self.vel_y = 15

        dy += self.vel_y

        #check collision 
        for tile in world.obstacle_list:
            #collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                #check if moving left or right
                if dx<0:  
                    dx = tile[1].right - self.rect.left
                    if self.char_type =='enemy':
                        self.direction *= -1
                        self.move_counter = 0
                elif dx > 0:
                    dx = tile[1].left - self.rect.right
                    if dy ==0:
                        self.in_air = False
            if tile[1].colliderect(self.rect.x, self.rect.y+dy+1, self.width, self.height):
                #check if moving up or down
                if self.vel_y<0:  
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom
                    self.in_air = False

       #check for collision with water 
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        #check for collision with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        #check if fallen off map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx =  0
                         
        self.rect.x += dx
        self.rect.y += dy

        #update scroll
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
                or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 8
            bullet = Bullet(self.rect.centerx + (0.8 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1
            shot_fx.play()


    def ai(self):
        if self.alive:
            if self.vision.colliderect(player.rect):
                self.update_action(0)
                if level ==3 and self.shoot_cooldown == 0: 
                    grenade_group.add(Grenade((self.rect.centerx + (0.5*self.rect.size[0]*self.direction)), self.rect.top, self.direction))
                    self.shoot_cooldown = 50
                else:
                    self.shoot()
                
            else: 
                if self.idling ==True:
                    if random.randint(1,self.idle_length) == 1:
                        self.idling = False
                
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1) #run
                    self.move_counter += 1

                    if random.randint(1,200) == 1:
                        self.idling=True
                        self.update_action(0) # 0 = idling                
            
                    if self.move_counter > self.ai_patrol_length:
                        self.direction *=-1
                        self.move_counter *=-1
            self.vision.center = (self.rect.centerx + self.vision.width/2 * self.direction, self.rect.centery)
        self.rect.x += screen_scroll
        
    def update_animation(self):
        #update animation
        ANIMATION_COOLDOWN = 100
        #update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        #check if new action is different to previous
        if new_action != self.action:
            self.action = new_action
            #update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        global lives
        global points
        if self.health <=0:
            if self.alive ==True and self.char_type == 'enemy':
                points+=5
                if level == 3:
                    points += 45
                    points += 50 * lives
            if self.alive ==True and self.char_type == 'player':
                lives-=1
            self.health = 0 
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        
        #health bars
        if self.char_type == 'enemy' and not level ==3:
            pygame.draw.rect(screen, BLACK, (self.rect.x, self.rect.top-20, self.rect.width+4, 14))
            pygame.draw.rect(screen, RED, (self.rect.x+2, self.rect.top-20+2, int(self.rect.width*(self.health/self.max_health)), 10))
        
class World():
    def __init__(self):
        self.obstacle_list = []
        
    def process_data(self, data):  
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >=0:
                    img=img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x*TILE_SIZE
                    img_rect.y = y*TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x*TILE_SIZE, y*TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x*TILE_SIZE, y*TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:
                        player = Soldier('player', x*TILE_SIZE, y*TILE_SIZE, 2, 5, 25, 5)
                        player_health_bar = HealthBar(SCREEN_WIDTH/12, 7, player.health, player.max_health)
                    elif tile == 16:
                        enemy = Soldier('enemy', x*TILE_SIZE, y*TILE_SIZE, 2, 3, 25, 0)
                        enemy_group.add(enemy)
                        if level ==3:
                            enemy_health_bar = HealthBar(SCREEN_WIDTH//2, 10, enemy.health, enemy.max_health)
                        else:
                            enemy_health_bar = 0
                    elif tile ==17:
                        item_box = ItemBox('Ammo', x*TILE_SIZE, y*TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile ==18:
                        item_box = ItemBox('Grenade', x*TILE_SIZE, y*TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile ==19:
                        item_box = ItemBox('Health', x*TILE_SIZE, y*TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile ==20:
                        exit = Exit(img, x*TILE_SIZE, y*TILE_SIZE)
                        exit_group.add(exit)
                        
        return player, player_health_bar, enemy_health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])
       
#Different classes for decoration, water, and exit because how the player interacts with them is different. 
class Decoration(pygame.sprite.Sprite): 
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x+TILE_SIZE //2, y+(TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
        
class Water(pygame.sprite.Sprite): 
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x+TILE_SIZE //2, y+(TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite): 
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x+TILE_SIZE //2, y+(TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class ItemBox(pygame.sprite.Sprite): 
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect= self.image.get_rect()
        self.rect.midtop = (x+TILE_SIZE //2, y+(TILE_SIZE - self.image.get_height()))
        
    def update(self):
        global points
        self.rect.x += screen_scroll
        #collision with player
        if pygame.sprite.collide_rect(self, player):
            #check which box
            if self.item_type == 'Health':
                player.health += 50
                points += 1
                if player.health >player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
                points += 1
            elif self.item_type == 'Grenade':
                player.grenades += 3
                points += 1
            
            self.kill()
           
class HealthBar:
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health #initial health
        self.max_health = max_health
        
    def draw(self, health):
        self.health = health #live health
        pygame.draw.rect(screen, BLACK, (self.x-self.max_health//2, self.y, self.max_health+4, 24))
        pygame.draw.rect(screen, RED, (self.x-self.max_health//2+2, self.y+2, int(self.max_health*(self.health/self.max_health)), 20))

class Bullet(pygame.sprite.Sprite): #sniper upgrade? different guns for each level?
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 20
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.rect.x += (self.direction * self.speed) + screen_scroll
        
        #check if bullet is out of bounds
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        #check collision with player
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 10
                self.kill()

        #check collision with enemy
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()

class Grenade(pygame.sprite.Sprite): #get the grenade throwing movement dependant on the players movement?? get the grenade to roll?
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 6
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction
        
    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y
        
        #check collision with floor
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x+dx, self.rect.y, self.width, self.height):
                self.direction *=-1
                dx = self.direction * self.speed
            if tile[1].colliderect(self.rect.x, self.rect.y+dy+1, self.width, self.height):
                #check if moving up
                if dy<0:
                    dy = tile[1].bottom - self.rect.top
                    self.vel_y *=-1
                #check if moving down
                elif dy >= 0:
                    dy = tile[1].top - self.rect.bottom
                    self.speed *= 0.75
                    self.vel_y*=-0.5
        
        dx = self.direction * self.speed

        #change grenade location
        self.rect.x += dx + screen_scroll
        self.rect.y += dy
        
        #count down timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            #damage to enemy and player
            self.player_distance = int(math.sqrt((pow((self.rect.centerx - player.rect.centerx),2) + pow((self.rect.centery - player.rect.centery),2)))) 
            if  self.player_distance < TILE_SIZE * 4:
                player.health -= TILE_SIZE * 4 - self.player_distance
            for enemy in enemy_group:
                self.enemy_distance = int(math.sqrt((pow((self.rect.centerx - enemy.rect.centerx),2) + pow((self.rect.centery - enemy.rect.centery),2)))) 
                if  self.enemy_distance < TILE_SIZE * 4:
                    enemy.health -= TILE_SIZE * 4 - self.enemy_distance             
                   
class Explosion(pygame.sprite.Sprite): 
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1,6):
            img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() *scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.counter = 0
        
    def update(self):
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 4 # how quickly it will animate
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            #check if animation is complete
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0
        
    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_HEIGHT:
            fade_complete=True
            
        return fade_complete

#screen fades
death_fade = ScreenFade(2, BLACK, 4) 
win_fade = ScreenFade(2, GOLD, 4)

#create buttons
start_button = button.Button(SCREEN_WIDTH // 2 - 130, int(SCREEN_HEIGHT*(3/8)), start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, int(SCREEN_HEIGHT*(5/8)), exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)

#create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

#create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
#load level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter= ',')
    for x,row in enumerate(reader):
        for y,tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
player, player_health_bar, enemy_health_bar = world.process_data(world_data)

run = True
while run:
    
    clock.tick(FPS)
    
    if start_game == False:
        screen.fill(BG)
        if start_button.draw(screen):
            start_game = True
        if exit_button.draw(screen):
            run = False
    else:
            
        draw_bg()
        #draw world map
        world.draw()
        
        player_health_bar.draw(player.health)
        if level ==3:
            for enemy in enemy_group:
                enemy_health_bar.draw(enemy.health)
    
        #ammo
        draw_text(f'AMMO: {player.ammo}', font, WHITE, 10, 35)
        #grenades
        draw_text(f'GRENADES: {player.grenades}', font, WHITE, 10, 60)
        #lives
        draw_text(f'Lives: {lives}', font, WHITE, 10, 85)
        #points 
        draw_text(f'{points}', big_font, WHITE, SCREEN_WIDTH-75, 10)
    
    
        player.update()
        player.draw()
        
        #update enemy before drawing
        for enemy in enemy_group:
            enemy.update()
            enemy.draw()
            enemy.ai()

    
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)
        
    
        #update player actions
        if player.alive:
            if shoot:
                player.shoot()
            elif grenade and grenade_thrown== False and player.grenades >0:
                grenade = Grenade(player.rect.centerx + (0.5*player.rect.size[0]*player.direction), player.rect.top, player.direction)
                grenade_group.add(grenade)
                grenade_thrown = True
                player.grenades -= 1
            if player.in_air:
                player.update_action(2)  #2 = jump
            elif left or right:
                player.update_action(1)  #1 = run
            else:
                player.update_action(0)  #0 = idle
            screen_scroll, level_complete = player.move(left, right)
            bg_scroll -= screen_scroll
            if level_complete:
                points+=10
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter= ',')
                        for x,row in enumerate(reader):
                            for y,tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar, enemy_health_bar = world.process_data(world_data)   
            
        else:
                screen_scroll = 0
                player.move(False, False)  #to stop player floating if they die in the air
                if death_fade.fade():
                    if lives == 0:
                        draw_text(f'You have no lives remaining', big_font, WHITE, SCREEN_WIDTH//6, int(SCREEN_HEIGHT*0.25))
                        draw_text(f'You scored {points} points!', big_font, WHITE, SCREEN_WIDTH//4, int(SCREEN_HEIGHT*0.25)+70)
                        if exit_button.draw(screen):
                            run = False
                    else:
                        if lives > 1:
                            draw_text(f'You have {lives} lives remaining', big_font, WHITE, SCREEN_WIDTH//5, int(SCREEN_HEIGHT*0.25))
                        elif lives == 1:
                            draw_text(f'You have {lives} life remaining', big_font, WHITE, SCREEN_WIDTH//5, int(SCREEN_HEIGHT*0.25))
                        if restart_button.draw(screen):
                            death_fade.fade_counter = 0
                            bg_scroll = 0
                            world_data = reset_level()
                            with open(f'level{level}_data.csv', newline='') as csvfile:
                                reader = csv.reader(csvfile, delimiter= ',')
                                for x,row in enumerate(reader):
                                    for y,tile in enumerate(row):
                                        world_data[x][y] = int(tile)
                    
                            world = World()
                            player, player_health_bar, enemy_health_bar = world.process_data(world_data)
    
    for enemy in enemy_group:
        if level ==3 and enemy.alive == False:
            if win_fade.fade():
                draw_text(f'You won with {lives} lives remaing!', big_font, WHITE, SCREEN_WIDTH//7, int(SCREEN_HEIGHT*0.25)-10)
                draw_text(f'+{lives*50}!', big_font, WHITE, SCREEN_WIDTH//7, int(SCREEN_HEIGHT*0.25)+30)
                draw_text(f'You scored {points} points!', big_font, WHITE, SCREEN_WIDTH//7, int(SCREEN_HEIGHT*0.25)+70)
                if exit_button.draw(screen):
                            run = False
        
    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False
        #keyboard presses
        if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    left = True
                if event.key == pygame.K_d:
                    right = True
                if event.key == pygame.K_q:
                    grenade = True
                if event.key == pygame.K_SPACE and player.ammo > 0:
                    shoot = True
                if event.key == pygame.K_w:
                    player.jump = True
                    jump_fx.play()
                if event.key == pygame.K_ESCAPE:
                    run = False

                #keyboard button release
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                left = False
            if event.key == pygame.K_d:
                right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False

    pygame.display.update()

pygame.quit()
