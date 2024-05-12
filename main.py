# Jumpster Sidehill
# Created by Höggva company
# Date of Creation: May 11, 2024
# Description:
# Jumpster Sidehill is a simple obstacle avoidance game where the player controls the main character
# that must jump over incoming obstacles. The game features increasing difficulty and is designed
# for quick casual gameplay.

import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 400
FPS = 60
DARK_GRAY = (51, 51, 51)  # Hex color #333333
WHITE = (255, 255, 255)
GROUND_HEIGHT = SCREEN_HEIGHT - 60
PLAYER_SIZE = 40
INITIAL_VELOCITY = 5
GRAVITY = 0.8
JUMP_HEIGHT = -15
FONT_SIZE = 24
SCORE_INCREMENT = 0.1  # Increment score based on this value

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jumpster Sidehill")
clock = pygame.time.Clock()
font = pygame.font.Font(None, FONT_SIZE)

# MainCharacter class
class MainCharacter:
    def __init__(self):
        self.rect = pygame.Rect(50, GROUND_HEIGHT - PLAYER_SIZE, PLAYER_SIZE, PLAYER_SIZE)
        self.jump_speed = JUMP_HEIGHT
        self.velocity = 0
        self.on_ground = True

    def update(self):
        self.velocity += GRAVITY
        self.rect.y += self.velocity

        if self.rect.bottom >= GROUND_HEIGHT:
            self.rect.bottom = GROUND_HEIGHT
            self.velocity = 0
            self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.velocity = self.jump_speed
            self.on_ground = False

# Obstacle class
class Obstacle:
    def __init__(self, x_offset):
        self.rect = pygame.Rect(SCREEN_WIDTH + x_offset, GROUND_HEIGHT - 20, 20, 40)
        self.active = True

    def update(self, velocity):
        if self.active:
            self.rect.x -= velocity

def check_collision(main_character, obstacles):
    for obstacle in obstacles:
        if main_character.rect.colliderect(obstacle.rect):
            return True
    return False

def display_score(score):
    score_surf = font.render(f"Score: {int(score)}", True, DARK_GRAY)
    screen.blit(score_surf, (SCREEN_WIDTH - score_surf.get_width() - 10, 10))

def display_pause():
    pause_surf = font.render("PAUSED", True, DARK_GRAY)
    screen.blit(pause_surf, (SCREEN_WIDTH // 2 - pause_surf.get_width() // 2, SCREEN_HEIGHT // 2 - pause_surf.get_height() // 2))

def restart_game(obstacles):
    global main_character, velocity, score, waiting_for_restart
    main_character = MainCharacter()
    obstacles.clear()
    append_obstacles(obstacles)
    velocity = INITIAL_VELOCITY
    score = 0
    waiting_for_restart = False

def append_obstacles(obstacles, count=1):
    last_x = obstacles[-1].rect.x if obstacles else 0
    for _ in range(count):
        spacing = random.randint(300, 600)
        obstacles.append(Obstacle(last_x + spacing))
        last_x += spacing

# Create game objects
main_character = MainCharacter()
obstacles = []
append_obstacles(obstacles, 3)  # Start with three obstacles
velocity = INITIAL_VELOCITY
paused = False
waiting_for_restart = True
score = 0

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if waiting_for_restart:
                    restart_game(obstacles)
                else:
                    main_character.jump()
            elif event.key == pygame.K_RETURN:
                paused = not paused

    if not paused and not waiting_for_restart:
        # Update game state
        main_character.update()
        for obstacle in obstacles:
            obstacle.update(velocity)

        # Remove inactive obstacles
        obstacles = [obstacle for obstacle in obstacles if obstacle.rect.x > -20]

        # Randomly add new obstacles
        if not obstacles or obstacles[-1].rect.x < SCREEN_WIDTH - 150:
            append_obstacles(obstacles, random.choice([1, 2, 3]))

        # Increase score
        score += SCORE_INCREMENT * velocity

        # Increase speed and difficulty gradually
        velocity += 0.0005

        # Check collision
        if check_collision(main_character, obstacles):
            waiting_for_restart = True

    # Draw everything
    screen.fill(WHITE)
    pygame.draw.line(screen, DARK_GRAY, (0, GROUND_HEIGHT), (SCREEN_WIDTH, GROUND_HEIGHT), 2)
    pygame.draw.rect(screen, DARK_GRAY, main_character.rect)
    for obstacle in obstacles:
        pygame.draw.rect(screen, DARK_GRAY, obstacle.rect)

    if paused:
        display_pause()
    if not waiting_for_restart:
        display_score(score)

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

# Clean up
pygame.quit()
sys.exit()

