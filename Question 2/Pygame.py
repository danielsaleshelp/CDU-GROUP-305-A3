import os
import math
import random
import csv


# try to open pygame
try:
    import pygame
except ImportError:  # if pygame is not installed, install it then open it
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
    import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Game')

clock = pygame.time.Clock()
FPS = 30
ROWS = 16
COLS = 150
TILE_TYPES = 21

level = 1

#define game variables
GRAVITY = 0.75
SCROLL_THRESH = 250
bg_scroll = 0
TILE_SIZE = SCREEN_HEIGHT //ROWS

#define player action variables
left = False
right = False
shoot = False
grenade = False
grenade_thrown = False

#load images
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

font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))
    

def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range (5):
        screen.blit(sky_img ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.ger_height() - 300))
        screen.blit(pine1_img((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.ger_height() - 150))
        screen.blit(pine2_img((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.ger_height()))
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
            if tile[1].colliderect(self.rect.x+dx, self.rect.y, self.width, self.height):
                #check if moving left or right
                if dx<0:  
                    dx = tile[1].right - self.rect.left
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

        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx =  0
                         
        self.rect.x += dx
        self.rect.y += dy

        #update scroll
        if self.char_type == 'player'
            if (self.rect.right > SCREEN_WIDTH - SCREEN_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
                or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 8
            bullet = Bullet(self.rect.centerx + (0.8 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1


    def ai(self):
        if self.alive:
            
            if self.vision.colliderect(player.rect):
                self.update_action(0)
                self.shoot()
            else: 
                if self.idling ==True:   
                    if random.randint(1,200) == 1:
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
                    self.vision.center = (self.rect.centerx + self.vision.width/2 * self.direction, self.rect.centery)

                    if random.randint(1,200) == 1:
                        self.idling=True
                        self.update_action(0) # 0 = idling                
            
                    if self.move_counter > TILE_SIZE:
                        self.direction *=-1
                        self.move_counter *=-1

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
        if self.health <=0:
            self.health = 0 
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        
        #health bars
        if self.char_type == 'enemy':
            pygame.draw.rect(screen, BLACK, (self.rect.x, self.rect.top-20, 54, 14))
            pygame.draw.rect(screen, RED, (self.rect.x+2, self.rect.top-20+2, int(50*(self.health/self.max_health)), 10))
        
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
                        water_group.add(decoration)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x*TILE_SIZE, y*TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:
                        player = Soldier('player', x*TILE_SIZE, y*TILE_SIZE, 2, 5, 25, 5)
                        health_bar = HealthBar(10, 10, player.health, player.max_health)
                    elif tile == 16:
                        enemy = Soldier('enemy', x*TILE_SIZE, y*TILE_SIZE, 2, 3, 25, 0)
                        enemy_group.add(enemy)
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
                        exit_group.add(decoration)
        return player, health_bar

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
        self.rect.midtop = (x+TILE_SIZE //2, y+(TILE_TYPES - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite): 
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x+TILE_SIZE //2, y+(TILE_TYPES - self.image.get_height()))

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
        self.rect.x += screen_scroll
        #collision with player
        if pygame.sprite.collide_rect(self, player):
            #check which box
            if self.item_type == 'Health':
                player.health += 25
                if player.health >player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3
            
            self.kill()
           
class HealthBar:
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health #initial health
        self.max_health = max_health
        
    def draw(self, health):
        self.health = health #live health
        
        pygame.draw.rect(screen, BLACK, (self.x, self.y, 154, 24))
        pygame.draw.rect(screen, RED, (self.x+2, self.y+2, int(150*(self.health/self.max_health)), 20))

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
player, health_bar = world.process_data(world_data)

run = True
while run:
    clock.tick(FPS)
    draw_bg()
    
    #draw world map
    world.draw()
    
    health_bar.draw(player.health)

    #tut part 7 if we want to display ammo and grenades with images instead of numbers
    #ammo
    draw_text(f'AMMO: {player.ammo}', font, WHITE, 10, 35)
    #grenades
    draw_text(f'GRENDADES: {player.grenades}', font, WHITE, 10, 60)


    player.update()
    player.draw()
    
    #update enemy before drawing
    for enemy in enemy_group:
        enemy.ai()
        enemy.update()
        enemy.draw()

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
            grenade = Grenade(player.rect.centerx + (0.5*player.rect.size[0]*player.direction),\
                              player.rect.top, player.direction)
            grenade_group.add(grenade)
            grenade_thrown = True
            player.grenades -= 1
        if player.in_air:
            player.update_action(2)  #2 = jump
        elif left or right:
            player.update_action(1)  #1 = run
        else:
            player.update_action(0)  #0 = idle
        screen_scroll = player.move(left, right)
        bg_scroll -= screen_scroll
    #to stop player floating if they die in the air
    if not player.alive:
        player.move(False, False)


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
