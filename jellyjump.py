import pygame
import sys
import random

pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(8)

jump_sound = pygame.mixer.Sound('assets/sounds/woohoo_sound.wav')
background_sound = pygame.mixer.Sound("assets/sounds/underwater_sound.wav")
coin_collect_sound = pygame.mixer.Sound("assets/sounds/coin_collect_sound.wav")

bg_channel = pygame.mixer.Channel(0)
jump_channel = pygame.mixer.Channel(1)
coin_collect_channel = pygame.mixer.Channel(2)

bg_channel.set_volume(0.2)
jump_channel.set_volume(1.0)
coin_collect_channel.set_volume(0.2)

bg_channel.play(background_sound, loops=-1)

font = pygame.font.Font("/Users/reine/Downloads/minecraftia/Minecraftia-Regular.ttf", 20)

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jelly Jump")
clock = pygame.time.Clock()
FPS = 60

background_img = pygame.image.load("assets/images/bg.png").convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

heart_img = pygame.image.load("assets/images/heart.png").convert_alpha()
heart_img = pygame.transform.scale(heart_img, (20, 20))

coin_img = pygame.image.load("assets/images/coin.png").convert_alpha()
coin_img = pygame.transform.scale(coin_img, (40, 40))

gravity = 0.4
velocity = 0
jumping = False
is_game_over = False
waiting_to_restart = False
score = 0
lives = 3

JELLY_SIZE = 60
jelly_color = (234, 143, 212)
jelly_rect = pygame.Rect(200, HEIGHT // 2 - JELLY_SIZE // 2, JELLY_SIZE, JELLY_SIZE)

OBSTACLE_WIDTH = 80
OBSTACLE_GAP = 180
OBSTACLE_SPEED = 3
BASE_OBSTACLE_SPEED = 3
BASE_SPAWN_INTERVAL = 145
obstacle_timer = 0
obstacles = []

bubble_color = (142, 224, 255)
bubbles = []

coins = []
coin_radius = 13
coins_count = 0

level = 1
level_start_time = None


def create_obstacle():
    top_height = random.randint(100, 300)
    bottom_y = top_height + OBSTACLE_GAP
    color = (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )

    obstacle = {
        "x": WIDTH,
        "top_height": top_height,
        "bottom_y": bottom_y,
        "color": color,
        "passed": False,
    }

    coin_y = random.randint(100, 500)
    coins.append({
        "x": WIDTH + OBSTACLE_WIDTH // 2 + 150,
        "y": coin_y,
        "collected": False
    })

    return obstacle


def draw_obstacles():
    for obs in obstacles:
        top_rect = pygame.Rect(obs["x"], 0, OBSTACLE_WIDTH, obs["top_height"])
        bottom_rect = pygame.Rect(obs["x"], obs["bottom_y"], OBSTACLE_WIDTH, HEIGHT - obs["bottom_y"])
        pygame.draw.rect(screen, obs["color"], top_rect)
        pygame.draw.rect(screen, obs["color"], bottom_rect)


def draw_coins():
    for coin in coins:
        if not coin["collected"]:
            screen.blit(coin_img, (int(coin["x"]), int(coin["y"])))


def check_passed_obstacles():
    global score
    for obs in obstacles:
        if jelly_rect.right > obs["x"] + OBSTACLE_WIDTH and not obs["passed"]:
            score += 1
            jump_channel.play(jump_sound)
            obs["passed"] = True


def check_coin_collisions():
    global coins_count
    for coin in coins:
        if not coin["collected"]:
            coin_rect = pygame.Rect(
                coin["x"] - coin_radius,
                coin["y"] - coin_radius,
                coin_radius * 2,
                coin_radius * 2
            )
            if jelly_rect.colliderect(coin_rect):
                coin["collected"] = True
                coins_count += 1
                coin_collect_channel.play(coin_collect_sound)


def lose_life():
    global lives, velocity, jumping, waiting_to_restart, is_game_over
    global obstacles, coins, OBSTACLE_SPEED, BASE_OBSTACLE_SPEED, BASE_SPAWN_INTERVAL

    lives -= 1
    jelly_rect.y = HEIGHT // 2 - JELLY_SIZE // 2
    velocity = 0
    jumping = False
    obstacles.clear()
    coins.clear()

    if lives <= 0:
        is_game_over = True
        waiting_to_restart = False
        OBSTACLE_SPEED = 3
        BASE_OBSTACLE_SPEED = 3
        BASE_SPAWN_INTERVAL = 145
        bg_channel.stop()
    else:
        waiting_to_restart = True


def reset_game():
    global velocity, jumping, is_game_over, waiting_to_restart
    global lives, obstacles, coins, score, coins_count
    global OBSTACLE_SPEED, BASE_OBSTACLE_SPEED, BASE_SPAWN_INTERVAL
    global level, level_start_time, obstacle_timer

    jelly_rect.y = HEIGHT // 2 - JELLY_SIZE // 2
    velocity = 0
    jumping = False
    is_game_over = False
    waiting_to_restart = False
    obstacles = []
    coins = []
    score = 0
    lives = 3
    OBSTACLE_SPEED = 3
    BASE_OBSTACLE_SPEED = 3
    BASE_SPAWN_INTERVAL = 145
    obstacle_timer = 0
    level = 1
    level_start_time = None
    coins_count = 0

    if not bg_channel.get_busy():
        bg_channel.play(background_sound, loops=-1)


def draw_bubbles():
    if random.randint(0, 10) == 0:
        x = random.randint(0, WIDTH)
        y = HEIGHT
        radius = random.randint(5, 10)
        speed = random.uniform(1, 2)
        bubbles.append({"x": x, "y": y, "radius": radius, "speed": speed})

    for bubble in bubbles[:]:
        bubble["y"] -= bubble["speed"]
        pygame.draw.circle(
            screen,
            bubble_color,
            (int(bubble["x"]), int(bubble["y"])),
            bubble["radius"]
        )
        if bubble["y"] + bubble["radius"] < 0:
            bubbles.remove(bubble)


def draw_jellyfish_face():
    eye_radius = 10
    left_eye_center = (jelly_rect.x + JELLY_SIZE // 4, jelly_rect.y + JELLY_SIZE // 4)
    right_eye_center = (jelly_rect.x + 3 * JELLY_SIZE // 4, jelly_rect.y + JELLY_SIZE // 4)

    pygame.draw.circle(screen, (255, 255, 255), left_eye_center, eye_radius)
    pygame.draw.circle(screen, (255, 255, 255), right_eye_center, eye_radius)
    pygame.draw.circle(screen, (0, 0, 0), left_eye_center, eye_radius // 2)
    pygame.draw.circle(screen, (0, 0, 0), right_eye_center, eye_radius // 2)

    pygame.draw.line(
        screen, jelly_color,
        (jelly_rect.left + 15, jelly_rect.bottom),
        (jelly_rect.left + 15, jelly_rect.bottom + 15), 2
    )
    pygame.draw.line(
        screen, jelly_color,
        (jelly_rect.centerx, jelly_rect.bottom),
        (jelly_rect.centerx, jelly_rect.bottom + 15), 2
    )
    pygame.draw.line(
        screen, jelly_color,
        (jelly_rect.right - 15, jelly_rect.bottom),
        (jelly_rect.right - 15, jelly_rect.bottom + 15), 2
    )

    mouth_rect = pygame.Rect(
        jelly_rect.x + JELLY_SIZE // 4,
        jelly_rect.y + 3 * JELLY_SIZE // 4,
        JELLY_SIZE // 2,
        10
    )
    pygame.draw.arc(screen, (0, 0, 0), mouth_rect, 3.14, 2 * 3.14, 2)


while True:
    screen.blit(background_img, (0, 0))
    draw_bubbles()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if not is_game_over:
                if event.key == pygame.K_SPACE:
                    if waiting_to_restart:
                        waiting_to_restart = False
                    velocity = -8
                    jumping = True
            else:
                if event.key == pygame.K_r:
                    reset_game()

    if not is_game_over:
        if not waiting_to_restart:
            velocity += gravity
            jelly_rect.y += int(velocity)

            if velocity > 0 and jumping:
                jumping = False

            if jelly_rect.top <= 0 or jelly_rect.bottom >= HEIGHT:
                lose_life()

            new_level = score // 5 + 1
            if new_level > level:
                level = new_level
                level_start_time = pygame.time.get_ticks()
                OBSTACLE_SPEED = BASE_OBSTACLE_SPEED + (level - 1)
                BASE_SPAWN_INTERVAL = max(60, 145 - (level - 1) * 10)

            spawn_interval = int(BASE_SPAWN_INTERVAL * BASE_OBSTACLE_SPEED / OBSTACLE_SPEED)
            obstacle_timer += 1

            if obstacle_timer > spawn_interval:
                obstacles.append(create_obstacle())
                obstacle_timer = 0

            for obs in obstacles:
                obs["x"] -= OBSTACLE_SPEED
            obstacles = [obs for obs in obstacles if obs["x"] + OBSTACLE_WIDTH > 0]

            for coin in coins:
                coin["x"] -= OBSTACLE_SPEED
            coins = [coin for coin in coins if coin["x"] + coin_radius > 0]

            check_passed_obstacles()
            check_coin_collisions()

            for obs in obstacles:
                top_rect = pygame.Rect(obs["x"], 0, OBSTACLE_WIDTH, obs["top_height"])
                bottom_rect = pygame.Rect(obs["x"], obs["bottom_y"], OBSTACLE_WIDTH, HEIGHT - obs["bottom_y"])

                if jelly_rect.colliderect(top_rect) or jelly_rect.colliderect(bottom_rect):
                    lose_life()
                    break

        if level_start_time is not None and pygame.time.get_ticks() - level_start_time < 2000:
            level_text = font.render(f"Level {level}! Keep Going!", True, (255, 255, 255))
            screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2 - 40))
        elif level_start_time is not None:
            level_start_time = None

    draw_obstacles()
    draw_coins()

    pygame.draw.ellipse(screen, jelly_color, jelly_rect)
    draw_jellyfish_face()

    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    coin_text = font.render(f"{coins_count}", True, (255, 255, 255))

    screen.blit(score_text, (20, 20))
    screen.blit(coin_img, (20, 50))
    screen.blit(coin_text, (70, 55))

    for i in range(lives):
        screen.blit(heart_img, (20 + i * 25, 90))

    if waiting_to_restart and not is_game_over:
        pause_text = font.render("Press SPACE to continue", True, (255, 255, 255))
        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 20))

    if is_game_over:
        text = font.render("Game Over - Press R to Restart", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 60))

    pygame.display.flip()
    clock.tick(FPS)