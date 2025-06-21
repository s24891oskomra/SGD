import pygame
import random
import sys
from pygame.locals import *

# Game Constants
WIDTH, HEIGHT = 400, 600
FPS = 60
CAR_WIDTH, CAR_HEIGHT = 50, 100
ENEMY_WIDTH, ENEMY_HEIGHT = 50, 100
ITEM_WIDTH, ITEM_HEIGHT = 25, 25
ROAD_COLOR = (50, 50, 50)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARKGRAY  = ( 40,  40,  40)


def main():
    global SCREEN, CLOCK, FONT, PLAYER_IMAGE, ENEMY_IMAGE,\
        UIFONT, HEALTH_ITEM_IMAGE, MUTE_IMAGE, UNMUTE_IMAGE,\
        COIN_IMAGE, BACKGROUND_IMAGE, PLAYER_MASK, ENEMY_MASK, HEALTH_MASK, COIN_MASK

    pygame.init()
    # Setup
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pixel Chaser")
    CLOCK = pygame.time.Clock()
    FONT = pygame.font.SysFont('freesansbold.ttf', 40)
    UIFONT = pygame.font.SysFont('freesansbold.ttf', 28)

    # Load images
    player_image = pygame.image.load("player_car.png")
    enemy_image = pygame.image.load("enemy_car.png")
    health_image = pygame.image.load("health_item.png")
    coin_image = pygame.image.load("coin.png")
    mute_image = pygame.image.load("mute.png")
    unmute_image = pygame.image.load("unmute.png")
    background_image = pygame.image.load("background.jpg")

    # Loud sounds
    pygame.mixer.init()
    pygame.mixer.music.load("background_music.mp3")

    # Scale images
    PLAYER_IMAGE = pygame.transform.scale(player_image, (CAR_WIDTH, CAR_HEIGHT))
    ENEMY_IMAGE = pygame.transform.scale(enemy_image, (ENEMY_WIDTH, ENEMY_HEIGHT))
    HEALTH_ITEM_IMAGE = pygame.transform.scale(health_image, (ITEM_WIDTH, ITEM_HEIGHT))
    COIN_IMAGE = pygame.transform.scale(coin_image, (ITEM_WIDTH, ITEM_HEIGHT))
    MUTE_IMAGE = pygame.transform.scale(mute_image, (50, 50))
    UNMUTE_IMAGE = pygame.transform.scale(unmute_image, (50, 50))
    BACKGROUND_IMAGE = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
    PLAYER_MASK = pygame.mask.from_surface(PLAYER_IMAGE)
    ENEMY_MASK = pygame.mask.from_surface(ENEMY_IMAGE)
    HEALTH_MASK = pygame.mask.from_surface(HEALTH_ITEM_IMAGE)
    COIN_MASK = pygame.mask.from_surface(COIN_IMAGE)

    showStartScreen()
    while True:
        runGame()


def runGame():
    # Player Setup
    player = pygame.Rect(WIDTH // 2 - CAR_WIDTH // 2, HEIGHT - 120, CAR_WIDTH, CAR_HEIGHT)
    player_speed = 5

    # Enemy Setup
    enemy_speed = 5
    enemies = []

    # Items setup
    health_speed = 5
    coin_speed = 5
    coins = []
    healthies = []

    # Game setup
    score_count = 0
    previous_score = 0
    health_count = 3
    level_count = 1
    enemy_spawn_timer = 0
    health_spawn_timer = 0
    coin_spawn_timer = 0
    running = True
    pygame.mixer.music.play(-1)
    car_crash_sound = pygame.mixer.Sound("crash_sound.mp3")
    game_over_sound = pygame.mixer.Sound("game_over_sound.mp3")
    game_win_sound = pygame.mixer.Sound("game_win_sound.mp3")
    coin_sound = pygame.mixer.Sound("coin_sound.mp3")

    while running:
        CLOCK.tick(FPS)
        drawBackground()
        drawPressPauseKeyMsg()
        drawPressMuteKeyMsg()

        # Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    showPauseScreen()
                if event.key == pygame.K_m:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()

        # Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= player_speed
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.x += player_speed
        # Spawning enemies
        enemy_spawn_timer += 1
        health_spawn_timer += 1
        coin_spawn_timer += 1
        if enemy_spawn_timer > 45:  # Adjust spawn rate
            spawn_enemy(enemies)
            enemy_spawn_timer = 0
        if health_spawn_timer > 480:
            spawn_health(healthies)
            health_spawn_timer = 0
        if coin_spawn_timer > 240:
            spawn_coin(coins)
            coin_spawn_timer = 0

        # Update enemies
        for enemy in enemies[:]:
            enemy.y += enemy_speed
            if enemy.top > HEIGHT:
                enemies.remove(enemy)
                score_count += 1
            # Level up
            if score_count >= previous_score + 5:
                level_count += 1
                enemy_speed += 0.5
                previous_score += 5
            # Collide
            offset = (enemy.x - player.x, enemy.y - player.y)
            if PLAYER_MASK.overlap(ENEMY_MASK, offset):
                car_crash_sound.play()
                enemies.remove(enemy)
                health_count -= 1

        #Update health items
        for health in healthies:
            health.y += health_speed
            if health.top > HEIGHT:
                healthies.remove(health)
            #Add health
            offset = (health.x - player.x, health.y - player.y)
            if PLAYER_MASK.overlap(HEALTH_MASK, offset):
                healthies.remove(health)
                health_count += 1

        #Update coin items
        for coin in coins:
            coin.y += coin_speed
            if coin.top > HEIGHT:
                coins.remove(coin)
            offset = (coin.x - player.x, coin.y - player.y)
            if PLAYER_MASK.overlap(COIN_MASK, offset):
                coin_sound.play()
                coins.remove(coin)
                score_count += 2



        # Game won
        if score_count >= 100:
            pygame.mixer.music.stop()
            game_win_sound.play()
            return showGameWinnerScreen()
        # Game lost
        if health_count <= 0:
            pygame.mixer.music.stop()
            game_over_sound.play()
            return showGameOverScreen()

        # Drawing
        SCREEN.blit(PLAYER_IMAGE, (player.x, player.y))
        for enemy in enemies:
            SCREEN.blit(ENEMY_IMAGE, (enemy.x, enemy.y))
        for health in healthies:
            SCREEN.blit(HEALTH_ITEM_IMAGE, (health.x, health.y))
        for coin in coins:
            SCREEN.blit(COIN_IMAGE, (coin.x, coin.y))

        if pygame.mixer.music.get_busy():
            SCREEN.blit(UNMUTE_IMAGE, (5, 525))
        else:
            SCREEN.blit(MUTE_IMAGE, (5, 525))



        score_text = UIFONT.render(f"Score: {score_count}", True, WHITE)
        health_text = UIFONT.render(f"Health: {health_count}", True, WHITE)
        level_text = UIFONT.render(f"Level: {level_count}", True, WHITE)
        SCREEN.blit(score_text, (10, 10))
        SCREEN.blit(level_text, (10, 40))
        SCREEN.blit(health_text, (305, 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


def spawn_enemy(enemies):
    x_pos = random.randint(0, WIDTH - ENEMY_WIDTH)
    enemy = pygame.Rect(x_pos, -ENEMY_HEIGHT, ENEMY_WIDTH, ENEMY_HEIGHT)
    enemies.append(enemy)


def spawn_health(healthies):
    x_post = random.randint(0, WIDTH - ITEM_WIDTH)
    health = pygame.Rect(x_post, -ITEM_HEIGHT, ITEM_WIDTH, ITEM_HEIGHT)
    healthies.append(health)


def spawn_coin(coins):
    x_post = random.randint(0, WIDTH - ITEM_WIDTH)
    coin = pygame.Rect(x_post, -ITEM_HEIGHT, ITEM_WIDTH, ITEM_HEIGHT)
    coins.append(coin)


def drawPressKeyMsg():
    pressKeySurf = FONT.render("Press any key to play", True, WHITE)
    SCREEN.blit(pressKeySurf, (WIDTH // 7.5, HEIGHT // 2))


def drawPressPauseKeyMsg():
    pauseFont = pygame.font.SysFont('freesansbold.ttf', 20)
    pressPauseKeySurf = pauseFont.render("Press p key to pause/unpause", True, WHITE)
    SCREEN.blit(pressPauseKeySurf, (WIDTH // 2, 570))


def drawPressMuteKeyMsg():
    muteFont = pygame.font.SysFont('freesansbold.ttf', 20)
    pressMuteKeySurf = muteFont.render("Press m key to mute music", True, WHITE)
    SCREEN.blit(pressMuteKeySurf, (5, 570))


def drawBackground():
    SCREEN.fill(DARKGRAY)

    line_width = 4
    line_height = 30
    gap = 30
    x_position = 100
    for x in range(3):
        for y in range(0, HEIGHT, line_height + gap):
            pygame.draw.rect(SCREEN, WHITE, (x_position, y, line_width, line_height))
        x_position += 100


def showStartScreen():
    titleFont = pygame.font.SysFont('freesansbold.ttf', 80)
    titleSurf = titleFont.render("Pixel Chaser", True, BLACK)

    while True:
        SCREEN.blit(BACKGROUND_IMAGE, (0, 0))
        SCREEN.blit(titleSurf, (25, HEIGHT // 4 ))
        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get()
            return
        pygame.display.update()
        CLOCK.tick(FPS)


def showGameOverScreen():
    gameOverFont = pygame.font.SysFont('freesansbold.ttf', 100)
    gameOverSurf = gameOverFont.render("Game Over", True, RED)

    SCREEN.blit(BACKGROUND_IMAGE, (0, 0))
    SCREEN.blit(gameOverSurf, (WIDTH // 60, HEIGHT // 4))
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress()

    while True:
        if checkForKeyPress():
            pygame.event.get()
            return


def showGameWinnerScreen():
    winnerFont = pygame.font.SysFont('freesansbold.ttf', 100)
    winnerSurf = winnerFont.render("You Win!", True, GREEN)

    SCREEN.blit(BACKGROUND_IMAGE, (0, 0))
    SCREEN.blit(winnerSurf, (WIDTH // 8, HEIGHT // 4))
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress()

    while True:
        if checkForKeyPress():
            pygame.event.get() 
            return


def showPauseScreen():
    pauseFont = pygame.font.SysFont('freesansbold.ttf', 80)
    pauseSurf = pauseFont.render("Game paused", True, RED)

    SCREEN.blit(BACKGROUND_IMAGE, (0, 0))
    SCREEN.blit(pauseSurf, (WIDTH // 40, HEIGHT // 3))
    drawPressPauseKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress()

    paused = True
    while paused:
        pygame.mixer.music.pause()
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_p:
                    paused = False
                    pygame.mixer.music.unpause()
        CLOCK.tick(5)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

