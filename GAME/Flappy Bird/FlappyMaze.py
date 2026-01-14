import pygame
import sys

pygame.init()

# ini adlah standar untuk membuat jendela di pygame
WIDTH, HEIGHT =  600 ,600
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Flappy with Maze")

Running = True #ini kondisi awal (variable awal)
# jalakan lopping biar jendela selalu terbuka
while Running:
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            Running = False

pygame.quit()
sys.exit()