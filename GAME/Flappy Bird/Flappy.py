import pygame
import random

pygame.init()

WIDTH, HEIGHT = 600, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)


font = pygame.font.Font(None, 36)

def draw_text(text, x, y, color=BLACK):
    """Menampilkan teks di layar."""
    label = font.render(text, True, color)
    SCREEN.blit(label, (x, y))

def play_game():
    global high_score

    BIRD_X = 50
    BIRD_Y = HEIGHT // 2
    BIRD_RADIUS = 15
    GRAVITY = 1
    JUMP_STRENGTH = -12
    bird_velocity = 0

    PIPE_WIDTH = 70
    pipe_speed = 3
    score = 0

    pipes = [] 

    for i in range(8): 
        pipe_height = random.randint(50, 400)
        pipe_gap = random.randint(120, 200) 
        pipe_x = WIDTH + (i * 200) 
        pipes.append([pipe_x, pipe_height, pipe_gap])

    running = True

    while running:
        SCREEN.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird_velocity = JUMP_STRENGTH

        bird_velocity += GRAVITY
        BIRD_Y += bird_velocity

        for pipe in pipes:
            pipe[0] -= pipe_speed

            if pipe[0] < -PIPE_WIDTH:
                pipe[0] = WIDTH
                pipe[1] = random.randint(50, 400) 
                pipe[2] = random.randint(120, 200) 
                score += 1
                high_score = max(high_score, score)

                if score % 5 == 0:
                    pipe_speed += 0.5

        for pipe in pipes:
            pipe_x, pipe_height, pipe_gap = pipe
            if BIRD_X + BIRD_RADIUS > pipe_x and BIRD_X - BIRD_RADIUS < pipe_x + PIPE_WIDTH:
                if BIRD_Y - BIRD_RADIUS < pipe_height or BIRD_Y + BIRD_RADIUS > pipe_height + pipe_gap:
                    running = False 

        if BIRD_Y >= HEIGHT or BIRD_Y <= 0:
            running = False 
        pygame.draw.circle(SCREEN, BLUE, (BIRD_X, BIRD_Y), BIRD_RADIUS)

        for pipe in pipes:
            pygame.draw.rect(SCREEN, GREEN, (pipe[0], 0, PIPE_WIDTH, pipe[1]))
            pygame.draw.rect(SCREEN, GREEN, (pipe[0], pipe[1] + pipe[2], PIPE_WIDTH, HEIGHT))

        draw_text(f"Skor: {score}", 10, 10)
        draw_text(f"High Score: {high_score}", 10, 40)

        pygame.display.update()
        pygame.time.delay(30)

    game_over_screen(score)

def game_over_screen(final_score):
    """Menampilkan layar game over."""
    SCREEN.fill(WHITE)
    
    draw_text("Game Over!", WIDTH // 2 - 60, HEIGHT // 3)
    draw_text(f"Skor Akhir: {final_score}", WIDTH // 2 - 60, HEIGHT // 3 + 40)
    draw_text(f"High Score: {high_score}", WIDTH // 2 - 60, HEIGHT // 3 + 80)

    text_restart = "Tekan SPACE untuk bermain lagi"
    text_width, _ = font.size(text_restart)
    draw_text(text_restart, (WIDTH - text_width) // 2, HEIGHT // 3 + 120)

    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                    play_game()

high_score = 0
play_game()
