import pygame
import sys
import random
import sqlite3

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 400
FPS = 60
DARK_GRAY = (51, 51, 51)
WHITE = (255, 255, 255)
GROUND_HEIGHT = SCREEN_HEIGHT - 60
PLAYER_SIZE = 40
INITIAL_VELOCITY = 6
GRAVITY = 1.18
JUMP_HEIGHT = -20
FAST_FALL_GRAVITY = 9.0
FONT_SIZE = 24

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jumpster Sidehill")
clock = pygame.time.Clock()
font = pygame.font.Font(None, FONT_SIZE)

class ScoreManager:
    def __init__(self):
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.setup_table()

    def setup_table(self):
        self.cursor.execute('CREATE TABLE scores (id INTEGER PRIMARY KEY, score INTEGER)')
        self.conn.commit()

    def add_score(self, score):
        self.cursor.execute('INSERT INTO scores (score) VALUES (?)', (score,))
        self.conn.commit()

    def get_top_scores(self, limit=5):
        self.cursor.execute('SELECT score FROM scores ORDER BY score DESC LIMIT ?', (limit,))
        return [score[0] for score in self.cursor.fetchall()]

    def close(self):
        self.conn.close()

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

    def fast_fall(self):
        if not self.on_ground:
            self.velocity += FAST_FALL_GRAVITY

class Obstacle:
    def __init__(self, x_offset):
        self.rect = pygame.Rect(SCREEN_WIDTH + x_offset, GROUND_HEIGHT - 20, 20, 40)
        self.active = True

    def update(self, velocity):
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
    screen.blit(pause_surf, ((SCREEN_WIDTH // 2 - pause_surf.get_width() // 2), (SCREEN_HEIGHT // 2 - pause_surf.get_height() // 2)))

def display_score_board(scores):
    screen.fill(WHITE)
    title_surf = font.render("Score Board", True, DARK_GRAY)
    screen.blit(title_surf, ((SCREEN_WIDTH // 2 - title_surf.get_width() // 2), 20))
    start_y = 100
    for score in scores:
        score_surf = font.render(f"Score: {score}", True, DARK_GRAY)
        screen.blit(score_surf, ((SCREEN_WIDTH // 2 - score_surf.get_width() // 2), start_y))
        start_y += 30

def display_game_over():
    game_over_surf = font.render("Game Over", True, DARK_GRAY)
    screen.blit(game_over_surf, ((SCREEN_WIDTH // 2 - game_over_surf.get_width() // 2), (SCREEN_HEIGHT // 2 - game_over_surf.get_height() // 2)))

def restart_game(score_manager, obstacles, scores, score):
    global velocity, waiting_for_restart, game_over
    score_manager.add_score(int(score))
    scores.append(int(score))
    main_character.__init__()
    obstacles.clear()
    append_obstacles(obstacles, 5)
    velocity = INITIAL_VELOCITY
    waiting_for_restart = True
    game_over = True

def append_obstacles(obstacles, count=1):
    last_x = obstacles[-1].rect.x if obstacles else 0
    min_spacing = random.randint(120, 150)
    max_spacing = random.randint(200, 400)
    for _ in range(count):
        spacing = random.randint(min_spacing, max_spacing)
        obstacles.append(Obstacle(last_x + spacing))
        last_x += spacing

# Create game objects
main_character = MainCharacter()
obstacles = []
score_manager = ScoreManager()
scores = []
append_obstacles(obstacles, 3)
velocity = INITIAL_VELOCITY
paused = False
waiting_for_restart = True
score = 0
show_scores = False
game_over = False

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            score_manager.close()
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if waiting_for_restart:
                    if game_over:
                        score = 0
                        game_over = False
                        waiting_for_restart = False
                    else:
                        restart_game(score_manager, obstacles, scores, score)
                else:
                    main_character.jump()
            elif event.key == pygame.K_DOWN:
                main_character.fast_fall()
            elif event.key == pygame.K_RETURN and not show_scores and not game_over:
                paused = not paused
            elif event.key == pygame.K_r and not game_over:
                show_scores = not show_scores
                if show_scores:
                    top_scores = score_manager.get_top_scores()
                    display_score_board(top_scores)

    if not paused and not waiting_for_restart and not show_scores and not game_over:
        # Update game state
        main_character.update()
        for obstacle in obstacles:
            obstacle.update(velocity)

        # Remove inactive obstacles
        obstacles = [obstacle for obstacle in obstacles if obstacle.rect.x > -20]

        # Randomly add new obstacles
        if not obstacles or obstacles[-1].rect.x < SCREEN_WIDTH - 300:  # Ensured a fair gap before new obstacles
            append_obstacles(obstacles, 1)

        # Increase score
        score += 0.1 * velocity

        # Increase speed and difficulty gradually
        velocity += 0.0005

        # Check collision
        if check_collision(main_character, obstacles):
            display_game_over()
            waiting_for_restart = True

    # Draw everything
    if not show_scores and not game_over:
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

