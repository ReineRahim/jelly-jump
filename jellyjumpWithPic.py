import pygame
import sys
import random

pygame.init()


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jelly Jump")
clock = pygame.time.Clock()
FPS = 60


background = pygame.image.load("background.png").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

jelly_normal = pygame.transform.scale(pygame.image.load("jelly_normal.png").convert_alpha(), (60, 60))
jelly_jump = pygame.transform.scale(pygame.image.load("jelly_jump.png").convert_alpha(), (60, 60))
jelly_crash = pygame.transform.scale(pygame.image.load("jelly_crash.png").convert_alpha(), (60, 60))


jelly_image = jelly_normal
jelly_rect = jelly_image.get_rect(center=(200, HEIGHT // 2))
gravity = 0.4
velocity = 0
jumping = False
is_game_over = False

score = 0

pass_sound = pygame.mixer.Sound("pass_sound.wav") 

OBSTACLE_WIDTH = 80
OBSTACLE_GAP = 180
OBSTACLE_SPEED = 3  
obstacle_timer = 0
obstacles = []


def create_obstacle():
    top_height = random.randint(100, 300)
    bottom_y = top_height + OBSTACLE_GAP
    return {
        "x": WIDTH,
        "top_height": top_height,
        "bottom_y": bottom_y
    }


def draw_obstacles():
    for obs in obstacles:
        top_rect = pygame.Rect(obs["x"], 0, OBSTACLE_WIDTH, obs["top_height"])
        bottom_rect = pygame.Rect(obs["x"], obs["bottom_y"], OBSTACLE_WIDTH, HEIGHT - obs["bottom_y"])

       
        for x in range(top_rect.left, top_rect.right, 10): 
            for y in range(top_rect.top, top_rect.bottom, 20):
                pygame.draw.rect(screen, (72, 209, 204), (x, y, 10, 20))  

        for x in range(bottom_rect.left, bottom_rect.right, 10):  
            for y in range(bottom_rect.top, bottom_rect.bottom, 20):
                pygame.draw.rect(screen, (60, 179, 113), (x, y, 10, 20)) 


def check_passed_obstacles():
    global score
    for obs in obstacles:
        if jelly_rect.right > obs["x"] + OBSTACLE_WIDTH and not obs.get("passed", False):
            score += 1  
            pass_sound.play()  
            obs["passed"] = True  


def reset_game():
    global jelly_rect, velocity, jumping, is_game_over, obstacles, jelly_image, score
    jelly_rect.center = (200, HEIGHT // 2)
    velocity = 0
    jumping = False
    is_game_over = False
    obstacles = []
    jelly_image = jelly_normal
    score = 0  


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if not is_game_over:
                if event.key == pygame.K_SPACE:
                    velocity = -8
                    jelly_image = jelly_jump
                    jumping = True
            else:
                if event.key == pygame.K_r:
                    reset_game()

    if not is_game_over:
        velocity += gravity
        jelly_rect.y += int(velocity)
        if velocity > 0 and jumping:
            jelly_image = jelly_normal
            jumping = False

        if jelly_rect.top <= 0 or jelly_rect.bottom >= HEIGHT:
            is_game_over = True
            jelly_image = jelly_crash

        
        obstacle_timer += 1
        if obstacle_timer > 150:  
            obstacles.append(create_obstacle())
            obstacle_timer = 0

        for obs in obstacles:
            obs["x"] -= OBSTACLE_SPEED

        obstacles = [obs for obs in obstacles if obs["x"] + OBSTACLE_WIDTH > 0]

        check_passed_obstacles()

        for obs in obstacles:
            top_rect = pygame.Rect(obs["x"], 0, OBSTACLE_WIDTH, obs["top_height"])
            bottom_rect = pygame.Rect(obs["x"], obs["bottom_y"], OBSTACLE_WIDTH, HEIGHT - obs["bottom_y"])
            if jelly_rect.colliderect(top_rect) or jelly_rect.colliderect(bottom_rect):
                is_game_over = True
                jelly_image = jelly_crash


    screen.blit(background, (0, 0))
    draw_obstacles()
    screen.blit(jelly_image, jelly_rect)

    font = pygame.font.SysFont("Arial", 36)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    if is_game_over:
        font = pygame.font.SysFont("Arial", 36)
        text = font.render("Game Over - Press R to Restart", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 40))

    pygame.display.flip()
    clock.tick(FPS)