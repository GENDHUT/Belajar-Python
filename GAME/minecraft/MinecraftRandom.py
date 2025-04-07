# Done kali?
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()
player = FirstPersonController()
Sky()

boxes = []
floating_up = False
float_speed = 0.1
default_speed = player.speed
run_speed = default_speed * 2
game_paused = False

# UI pause menu 
pause_text = Text(
    text='Q untuk keluar\nR untuk random map ulang',
    origin=(0,0),
    scale=2,
    enabled=False
)

def generate_world():
    global boxes, ground_size
    for box in boxes:
        destroy(box)
    boxes.clear()

    ground_size = random.randint(30, 60)
    print(f'Ukuran tanah: {ground_size}x{ground_size}')

    # Tanah
    for i in range(ground_size):
        for j in range(ground_size):
            box = Button(
                color=color.white,
                model='cube',
                position=(j, 0, i),
                texture='grass.png',
                parent=scene,
                origin_y=0.5
            )
            boxes.append(box)

    # Pohon
    tree_count = random.randint(ground_size // 4, ground_size // 2)
    for _ in range(tree_count):
        x = random.randint(1, ground_size - 2)
        z = random.randint(1, ground_size - 2)
        generate_tree(x, z)

def generate_tree(x, z):
    for y in range(1, 4):
        trunk = Button(
            model='cube',
            color=color.brown,
            texture='white_cube',
            position=(x, y, z),
            parent=scene,
            origin_y=0.5
        )
        boxes.append(trunk)

    leaf_offsets = [
        (0, 3, 0), (-1, 3, 0), (1, 3, 0),
        (0, 3, -1), (0, 3, 1),
        (0, 4, 0)
    ]
    for offset in leaf_offsets:
        leaf = Button(
            model='cube',
            color=color.green,
            texture='white_cube',
            position=(x + offset[0], offset[1], z + offset[2]),
            parent=scene,
            origin_y=0.5
        )
        boxes.append(leaf)

generate_world()

def input(key):
    global floating_up, game_paused
# Paused
    if key == 'escape':
        game_paused = not game_paused
        pause_text.enabled = game_paused
        player.enabled = not game_paused

    if game_paused:
        if key == 'q':
            application.quit()
        elif key == 'r':
            generate_world()
            game_paused = False
            pause_text.enabled = False
            player.enabled = True
        return  
# CTRL Untuk Float
    if key in ['left control', 'right control']:
        floating_up = True
        player.gravity = 0
    if key in ['left control up', 'right control up']:
        floating_up = False
        player.gravity = 1
# Shift untuk Speed Karakter
    if key in ['left shift', 'right shift']:
        player.speed = run_speed
    if key in ['left shift up', 'right shift up']:
        player.speed = default_speed

    for box in boxes:
        if box.hovered:
            if key == 'left mouse down':
                new = Button(
                    color=box.color,
                    model='cube',
                    position=box.position + mouse.normal,
                    texture=box.texture,
                    parent=scene,
                    origin_y=0.5
                )
                boxes.append(new)
            if key == 'right mouse down':
                boxes.remove(box)
                destroy(box)

def update():
    if not game_paused and floating_up:
        player.y += float_speed

app.run()
