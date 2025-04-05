import pygame
import random
import sys
import time

pygame.init()

# Ukuran 
TILE_SIZE = 20
COLS, ROWS = 40, 40 
WIDTH, HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Pac-Man AI Power Pellets")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)

BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)
MAGENTA = (255, 0, 255)

maze = [["1" for _ in range(COLS)] for _ in range(ROWS)]
dots = [[0 for _ in range(COLS)] for _ in range(ROWS)]

def generate_maze():
    for y in range(ROWS):
        for x in range(COLS):
            maze[y][x] = "1"
            dots[y][x] = 0

    visited = [[False for _ in range(COLS)] for _ in range(ROWS)]
    
    def is_valid(x, y):
        return 0 < x < COLS-1 and 0 < y < ROWS-1

    def carve(x, y):
        visited[y][x] = True
        maze[y][x] = "0"
        dots[y][x] = 1
        dirs = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny) and not visited[ny][nx]:
                wall_x, wall_y = x + dx//2, y + dy//2
                maze[wall_y][wall_x] = "0"
                dots[wall_y][wall_x] = 1
                carve(nx, ny)
    carve(1, 1)

generate_maze()

pacman_x, pacman_y = 1, 1
score = 0
pacman_slow = False
slow_timer = 0

power_pellets = []
last_pellet_spawn = time.time()
pellet_duration = 5
effects = {
    "eat_enemies": False,
    "freeze_enemies": False,
}
effect_timers = {"eat_enemies": 0, "freeze_enemies": 0}

bot_colors = [RED, CYAN, MAGENTA, GREEN, WHITE]
enemies = []

def spawn_enemy(color):
    while True:
        x, y = random.randint(1, COLS-2), random.randint(1, ROWS-2)
        if maze[y][x] == "0" and (x, y) != (pacman_x, pacman_y):
            return {"x": x, "y": y, "color": color}

def spawn_all_enemies():
    global enemies
    enemies = [spawn_enemy(c) for c in bot_colors]

spawn_all_enemies()

def draw_maze():
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if maze[y][x] == "1":
                pygame.draw.rect(screen, BLUE, rect)
            elif dots[y][x]:
                pygame.draw.circle(screen, WHITE, rect.center, 3)

def draw_pacman():
    center = (pacman_x * TILE_SIZE + TILE_SIZE // 2, pacman_y * TILE_SIZE + TILE_SIZE // 2)
    pygame.draw.circle(screen, YELLOW, center, TILE_SIZE // 2 - 2)

def draw_enemies():
    for enemy in enemies:
        center = (enemy["x"] * TILE_SIZE + TILE_SIZE // 2, enemy["y"] * TILE_SIZE + TILE_SIZE // 2)
        pygame.draw.circle(screen, enemy["color"], center, TILE_SIZE // 2 - 2)

def draw_score():
    text = font.render(f"Skor: {score}", True, WHITE)
    screen.blit(text, (10, HEIGHT - 30))

def draw_power_pellets():
    for pellet in power_pellets:
        if pellet["type"] == "eat":
            color = RED
        elif pellet["type"] == "freeze":
            color = BLUE
        elif pellet["type"] == "slow":
            color = GREEN
        else:
            color = WHITE
        rect = pygame.Rect(pellet["x"] * TILE_SIZE, pellet["y"] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.circle(screen, color, rect.center, TILE_SIZE // 2 - 4)

def move_pacman(dx, dy):
    global pacman_x, pacman_y, score
    nx, ny = pacman_x + dx, pacman_y + dy
    if maze[ny][nx] == "0":
        pacman_x, pacman_y = nx, ny
        if dots[ny][nx]:
            dots[ny][nx] = 0
            score += 10

def move_enemies():
    for enemy in enemies:
        if effects["freeze_enemies"]:
            continue 
        dx = dy = 0
        if abs(enemy["x"] - pacman_x) > abs(enemy["y"] - pacman_y):
            dx = -1 if enemy["x"] > pacman_x else 1
        else:
            dy = -1 if enemy["y"] > pacman_y else 1
        nx, ny = enemy["x"] + dx, enemy["y"] + dy
        if maze[ny][nx] == "0":
            enemy["x"], enemy["y"] = nx, ny

def spawn_power_pellet():
    types = ["eat", "freeze", "slow"]
    while True:
        x, y = random.randint(1, COLS-2), random.randint(1, ROWS-2)
        if maze[y][x] == "0":
            pellet_type = random.choice(types)
            power_pellets.append({"x": x, "y": y, "type": pellet_type, "spawn_time": time.time()})
            break

def check_power_pellet():
    global power_pellets, pacman_slow, slow_timer
    for pellet in power_pellets[:]:
        if pellet["x"] == pacman_x and pellet["y"] == pacman_y:
            if pellet["type"] == "eat":
                effects["eat_enemies"] = True
                effect_timers["eat_enemies"] = time.time()
            elif pellet["type"] == "freeze":
                effects["freeze_enemies"] = True
                effect_timers["freeze_enemies"] = time.time()
            elif pellet["type"] == "slow":
                pacman_slow = True
                slow_timer = time.time()
            power_pellets.remove(pellet)

def check_collision():
    global score
    for enemy in enemies:
        if enemy["x"] == pacman_x and enemy["y"] == pacman_y:
            if effects["eat_enemies"]:
                enemy.update(spawn_enemy(enemy["color"]))
                score += 100
            else:
                return True
    return False

def game_over_menu():
    """Menampilkan menu game over dengan opsi R untuk restart dan Q untuk quit."""
    menu_active = True
    while menu_active:
        screen.fill(BLACK)
        over_text = font.render("Game Over!", True, WHITE)
        restart_text = font.render("Tekan R untuk restart atau Q untuk keluar", True, WHITE)
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    menu_active = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def main():
    global last_pellet_spawn, effects, pacman_slow
    running = True
    while running:
        delay = 5 if pacman_slow else 10
        clock.tick(delay)
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            move_pacman(-1, 0)
        elif keys[pygame.K_RIGHT]:
            move_pacman(1, 0)
        elif keys[pygame.K_UP]:
            move_pacman(0, -1)
        elif keys[pygame.K_DOWN]:
            move_pacman(0, 1)

        move_enemies()
        check_power_pellet()

        now = time.time()
        if now - last_pellet_spawn >= 5:
            spawn_power_pellet()
            last_pellet_spawn = now

        if effects["eat_enemies"] and now - effect_timers["eat_enemies"] > pellet_duration:
            effects["eat_enemies"] = False
        if effects["freeze_enemies"] and now - effect_timers["freeze_enemies"] > pellet_duration:
            effects["freeze_enemies"] = False
        if pacman_slow and now - slow_timer > pellet_duration:
            pacman_slow = False

        if check_collision():
            game_over_menu()
            generate_maze()
            reset()

        draw_maze()
        draw_pacman()
        draw_enemies()
        draw_score()
        draw_power_pellets()
        pygame.display.update()

    pygame.quit()
    sys.exit()

def reset():
    global pacman_x, pacman_y, score, effects, pacman_slow, power_pellets
    pacman_x, pacman_y = 1, 1
    score = 0
    effects = {"eat_enemies": False, "freeze_enemies": False}
    pacman_slow = False
    power_pellets.clear()
    spawn_all_enemies()

if __name__ == "__main__":
    main()
