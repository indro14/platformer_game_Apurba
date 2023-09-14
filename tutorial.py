import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("2dsketch")  #Caption on top of the window

WIDTH, HEIGHT = 1000, 800    #screen size
PLAYER_VEL = 4     #speed of player
FPS = 70      #frame rate


window = pygame.display.set_mode((WIDTH, HEIGHT))    # it will creat a pygame window


def flip(sprites):   #flip every image according to the direction
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]  # true means flip in x direction false
                                                                              # meas don't fli y direction


def load_sprite_sheets(dir1, dir2, width, height, direction=False):  #load all different spritesheets
    path = join("assets", dir1, dir2)  #entering the path
    images = [f for f in listdir(path) if isfile(join(path, f))]  #load every file inside the directory

    all_sprites = {}   #allsprite into dictionary

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()  #append the image,alpha to load transparent image

        sprites = []
        for i in range(sprite_sheet.get_width() // width):  #image range
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)  #width of single image is 32
            rect = pygame.Rect(i * width, 0, width, height)  #i*32
            surface.blit(sprite_sheet, (0, 0), rect)   #draw sprite sheet
            sprites.append(pygame.transform.scale2x(surface))  #2X bigger size which means 64/64

        if direction:   #for multidirectional animation,need to put 2 keys
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):   #get block function
    path = join("assets", "Terrain", "Terrain.png")   #find the block
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)    #position of the image for the block
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):   #using sprites for good collision
    COLOR = (255, 0, 0)
    GRAVITY = 1   #for y velocity to make it more realistic
    SPRITES = load_sprite_sheets("MainCharacters", "Raya",  32, 32, True)  #load the sprite sheet, true for multidirection
    ANIMATION_DELAY = 4

    def __init__(self, x, y, width, height):  #initialize player with size
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)  #put width and height in rect to make it easy to move and collision
        self.x_vel = 0
        self.y_vel = 0   #player velocity, it'll keep moving untill remove the velocity
        self.mask = None
        self.direction = "left"  #animation direction
        self.animation_count = 0
        self.fall_count = 0   #how long have been falling
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8   #negetive because it'll jump up
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:   #double jumping
            self.fall_count = 0   #after jump resetting the fall count to 0

    def move(self, dx, dy):   # displacement in x and y direction
        self.rect.x += dx
        self.rect.y += dy



    def move_left(self, vel):   #to move left
        self.x_vel = -vel    # negetive velocity means left cz substract from x position
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel   # positive velocity means left
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def make_hit(self):
        self.hit = True

    def loop(self, fps):  #call everyframe, move the character in correct direction continuesly
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)  #adding gravity in y velocity
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1   #increment every loop
        self.update_sprite()

    def landed(self):
        self.fall_count = 0   #reset the gravity
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1  #if hit the head reverse the velosity

    def update_sprite(self):
        sprite_sheet = "idle"  #defult spritesheet, just standing and doing nothing
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"   #put animation in jump sequence
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"   #put animation in double jump sequence
        elif self.y_vel > self.GRAVITY * 2:   #low amount of gravity when on the block,reset the gravity
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"   #if have some velocity, it'll run ;animation

        sprite_sheet_name = sprite_sheet + "_" + self.direction   #direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)  #animation count /5(from variable).every 5 frm show different sprite
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)   #mapping pixels according to the images also for pixxel based collision

    def draw(self, win, offset_x):     #draw updated sprit on the screen
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)  #modify the image
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))   #this draw function automatticaly draw it on screen


class Block(Object):   #for blocks
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))  #at position 0,0
        self.mask = pygame.mask.from_surface(self.image)   #pixel collision


class Fire(Object):   #for traps
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height):   #it'll be animation
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):   #on from the asset
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):   #same as player loop
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):   #to avoid big count so make it limited
            self.animation_count = 0


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))  #load background image
    _, _, width, height = image.get_rect()   #_, _, means x and y..
    tiles = []   #background image will be organised as a tiles

    for i in range(WIDTH // width + 1):   #how many tiles will be need to fill the background +1 to leave no gap
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)   #placing the tiles imagesfrom left corner
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x):   #draw backgrounds,players,objects
    for tile in background:     #looping every tiles in background
        window.blit(bg_image, tile)    #fill the screen with tiles

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):   #for y position collision
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):  #colliding player with the obj
            if dy > 0:  #if going down on the screen
                player.rect.bottom = obj.rect.top   #bottom of the player and top of the object
                player.landed()
            elif dy < 0:   #if going up
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):   #horizontal collision
    player.move(dx, 0)  #to check if they were move to the r or l, would they hit a block
    player.update()   #updating the mask
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)   #reverse the movement
    player.update()
    return collided_object


def handle_move(player, objects):   #to make the movement into the function
    keys = pygame.key.get_pressed()

    player.x_vel = 0  #it'll move untill it's velocity set back to 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)  #*2 for leave some space btwn player and obj
    collide_right = collide(player, objects, PLAYER_VEL * 2)
                                                             #if collide won't move
    if keys[pygame.K_LEFT] and not collide_left:   #movement based on current position
        player.move_left(PLAYER_VEL)   #select key
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)  #select key

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()


def main(window):    #to run the game
    clock = pygame.time.Clock()
    background, bg_image = get_background("sketchbg.png")   #select image for background tiles

    block_size = 96

    player = Player(100, 100, 50, 50)
    fire = Fire(200, HEIGHT - block_size - 64, 16, 32)
    additional_fires = [
        Fire(-300, HEIGHT - block_size - 64, 16, 32),
        Fire(block_size*6, HEIGHT - block_size - 64, 16, 32),
        # Add extra fire
    ]

    fire.on()

    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]  #creating blocks from screen to left and right
    objects = [*floor, Block(block_size * 4, HEIGHT - block_size * 2, block_size),
               Block(block_size * 6, HEIGHT - block_size * 4, block_size), fire,]  #extra objects

    additional_blocks = [
        Block(block_size * 8, HEIGHT - block_size * 6, block_size),
        Block(block_size * 9, HEIGHT - block_size * 6, block_size),
        Block(block_size * 10, HEIGHT - block_size * 6, block_size),
        Block(block_size * 11, HEIGHT - block_size * 6, block_size),
        Block(-block_size * 13, HEIGHT - block_size * 2, block_size),
        Block(-block_size * 14, HEIGHT - block_size * 2, block_size),
        Block(-block_size * 15, HEIGHT - block_size * 2, block_size),
        Block(-block_size * 16, HEIGHT - block_size * 2, block_size)
        ]


    # Add the additional blocks and fires to the objects list
    objects.extend(additional_blocks)
    objects.extend(additional_fires)



    offset_x = 0
    scroll_area_width = 200

    run = True     #while loop to continually loop and act as our event loop
    while run:
        clock.tick(FPS)   #this loop gonna run in 60 fps

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break   #break this loop if want to quite

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and player.jump_count < 2:  #jump 2 times
                    player.jump()

        player.loop(FPS)
        fire.loop()  #call the loop function

        handle_move(player, objects)  #
        draw(window, background, bg_image, player, objects, offset_x)   #pass things to the game

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):    #scroll area width = 200 pixels means when it reaches
            # this level screen start scrolling
            offset_x += player.x_vel

    pygame.quit()
    quit()


if __name__ == "__main__":   #only call the main funtion if run this file directly
    main(window)