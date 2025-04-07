# V1 Update
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()
player = FirstPersonController()
Sky()

boxes = []
ground_size = 20

# Generate tanah
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

# Melayang.
floating_up = False
float_speed = 0.1

# Lari
default_speed = player.speed
run_speed = default_speed * 2

# fungsi pohon
def generate_tree(x, z):
    # Batang pohon
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

    # Daun
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

# pohon acak
for _ in range(10):
    x = random.randint(1, ground_size - 2)
    z = random.randint(1, ground_size - 2)
    generate_tree(x, z)

def input(key):
    global floating_up
    if key in ['left control', 'right control']:
        floating_up = True
        player.gravity = 0
    if key in ['left control up', 'right control up']:
        floating_up = False
        player.gravity = 1

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
    if floating_up:
        player.y += float_speed

app.run()
