import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 600, 600
BLOCK_SIZE = 20 
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)

clock = pygame.time.Clock()
SNAKE_SPEED = 15

font_style = pygame.font.SysFont("arial", 25)
score_font = pygame.font.SysFont("arial", 20)

def draw_snake(block_size, snake_list):
    """Menggambar setiap blok ular di layar berdasarkan koordinat di snake_list."""
    for block in snake_list:
        pygame.draw.rect(screen, GREEN, [block[0], block[1], block_size, block_size])

def display_message(msg, color):
    """Menampilkan pesan pada layar di tengah-tengah."""
    mesg = font_style.render(msg, True, color)
    text_width = mesg.get_width()
    text_height = mesg.get_height()
    screen.blit(mesg, [(WIDTH - text_width) / 2, (HEIGHT - text_height) / 2])

def show_score(score):
    """Menampilkan skor di pojok kanan atas."""
    score_text = score_font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, [WIDTH - 100, 10])

def game_loop():
    game_over = False
    game_close = False

    x = WIDTH / 2
    y = HEIGHT / 2

    x_change = 0
    y_change = 0

    snake_list = []
    snake_length = 1

    food_x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
    food_y = round(random.randrange(0, HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE

    score = 0

    direction = "STOP"  

    while not game_over:

        while game_close:
            screen.fill(BLACK)
            display_message("Kamu kalah! Tekan C untuk main lagi atau Q untuk keluar", RED)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and direction != "RIGHT":
                    x_change = -BLOCK_SIZE
                    y_change = 0
                    direction = "LEFT"
                elif event.key == pygame.K_RIGHT and direction != "LEFT":
                    x_change = BLOCK_SIZE
                    y_change = 0
                    direction = "RIGHT"
                elif event.key == pygame.K_UP and direction != "DOWN":
                    y_change = -BLOCK_SIZE
                    x_change = 0
                    direction = "UP"
                elif event.key == pygame.K_DOWN and direction != "UP":
                    y_change = BLOCK_SIZE
                    x_change = 0
                    direction = "DOWN"

        if x >= WIDTH or x < 0 or y >= HEIGHT or y < 0:
            game_close = True

        x += x_change
        y += y_change

        screen.fill(BLACK)
        pygame.draw.rect(screen, RED, [food_x, food_y, BLOCK_SIZE, BLOCK_SIZE])

        snake_head = [x, y]
        snake_list.append(snake_head)
        if len(snake_list) > snake_length:
            del snake_list[0]

        for block in snake_list[:-1]:
            if block == snake_head:
                game_close = True

        draw_snake(BLOCK_SIZE, snake_list)
        show_score(score)
        pygame.display.update()

        if x == food_x and y == food_y:
            food_x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            food_y = round(random.randrange(0, HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            snake_length += 1
            score += 10

        clock.tick(SNAKE_SPEED)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()
