import pygame
import random

pygame.init()

WIDTH, HEIGHT = 300, 600
BLOCK_SIZE = 30

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (169, 169, 169)
COLORS = [
    (0, 255, 255), (0, 0, 255), (255, 165, 0), 
    (255, 255, 0), (0, 255, 0), (128, 0, 128), (255, 0, 0)
]

SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]]   # J
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

class Tetris:
    def __init__(self):
        self.grid = [[BLACK for _ in range(WIDTH // BLOCK_SIZE)] for _ in range(HEIGHT // BLOCK_SIZE)]
        self.current_piece = self.new_piece()
        self.score = 0
        self.game_over = False

    def new_piece(self):
        shape = random.choice(SHAPES)
        color = random.choice(COLORS)
        return {
            "shape": shape,
            "color": color,
            "x": WIDTH // BLOCK_SIZE // 2 - len(shape[0]) // 2,
            "y": 0
        }

    def draw_grid(self):
        for y, row in enumerate(self.grid):
            for x, color in enumerate(row):
                pygame.draw.rect(screen, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, GRAY, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

    def draw_piece(self):
        for y, row in enumerate(self.current_piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    px = (self.current_piece["x"] + x) * BLOCK_SIZE
                    py = (self.current_piece["y"] + y) * BLOCK_SIZE
                    pygame.draw.rect(screen, self.current_piece["color"], (px, py, BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(screen, GRAY, (px, py, BLOCK_SIZE, BLOCK_SIZE), 1)

    def check_collision(self, dx=0, dy=0, rotated_shape=None):
        shape = rotated_shape if rotated_shape else self.current_piece["shape"]
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    nx = self.current_piece["x"] + x + dx
                    ny = self.current_piece["y"] + y + dy
                    if nx < 0 or nx >= WIDTH // BLOCK_SIZE or ny >= HEIGHT // BLOCK_SIZE:
                        return True
                    if ny >= 0 and self.grid[ny][nx] != BLACK:
                        return True
        return False

    def merge_piece(self):
        for y, row in enumerate(self.current_piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece["y"] + y][self.current_piece["x"] + x] = self.current_piece["color"]
        self.clear_lines()
        self.current_piece = self.new_piece()
        if self.check_collision():
            self.game_over = True

    def clear_lines(self):
        new_grid = [row for row in self.grid if BLACK in row]
        lines_cleared = len(self.grid) - len(new_grid)
        self.score += lines_cleared * 100
        self.grid = [[BLACK for _ in range(WIDTH // BLOCK_SIZE)] for _ in range(lines_cleared)] + new_grid

    def rotate_piece(self):
        rotated = list(zip(*self.current_piece["shape"][::-1]))
        if not self.check_collision(rotated_shape=rotated):
            self.current_piece["shape"] = rotated

    def move(self, dx, dy):
        if not self.check_collision(dx, dy):
            self.current_piece["x"] += dx
            self.current_piece["y"] += dy
        elif dy > 0:
            self.merge_piece()

    def draw_score(self):
        score_text = font.render(f"Skor: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

    def update(self):
        screen.fill(BLACK)
        self.draw_grid()
        self.draw_piece()
        self.draw_score()
        pygame.display.update()

    def reset(self):
        self.__init__()

def game_over_screen():
    over_text = font.render("GAME OVER", True, WHITE)
    restart_text = font.render("Tekan R untuk main lagi", True, WHITE)
    quit_text = font.render("Tekan Q untuk keluar", True, WHITE)
    screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 60))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 - 20))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 20))
    pygame.display.update()

def main():
    game = Tetris()
    drop_timer = 0
    drop_interval = 1000
    running = True

    while running:
        dt = clock.tick(30)
        drop_timer += dt
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if game.game_over:
                    if event.key == pygame.K_r:
                        game.reset()
                        drop_timer = 0
                        drop_interval = 1000
                    elif event.key == pygame.K_q:
                        running = False
                else:
                    if event.key == pygame.K_LEFT:
                        game.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        game.move(1, 0)
                    elif event.key == pygame.K_DOWN:
                        game.move(0, 1)
                    elif event.key == pygame.K_UP:
                        game.rotate_piece()

        if not game.game_over and drop_timer >= drop_interval:
            game.move(0, 1)
            drop_timer = 0

        drop_interval = max(200, 1000 - (game.score // 1000) * 100)

        game.update()

        if game.game_over:
            game_over_screen()

    pygame.quit()

if __name__ == "__main__":
    main()
