# Ori code update edit dikit
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
app = Ursina()
player = FirstPersonController()
Sky()

boxes = []
for i in range(20):
  for j in range(20):
    box = Button(color=color.white, model='cube', position=(j,0,i),
          texture='grass.png', parent=scene, origin_y=0.5)
    boxes.append(box)
game_paused = False
pause_text = Text(
    text='Q untuk keluar\nR untuk random map ulang',
    origin=(0,0),
    scale=2,
    enabled=False
)

def input(key):
  global game_paused
  for box in boxes:
    if box.hovered:
      if key == 'left mouse down':
        new = Button(color=color.white, model='cube', position=box.position + mouse.normal,
                    texture='grass.png', parent=scene, origin_y=0.5)
        boxes.append(new)
      if key == 'right mouse down':
        boxes.remove(box)
        destroy(box)
        
  if key == 'escape':
      game_paused = not game_paused
      pause_text.enabled = game_paused
      player.enabled = not game_paused
  if key == 'q':
      application.quit()
      if game_paused:
          if key == 'r':
              print("tes")
              game_paused = False
              pause_text.enabled = False
              player.enabled = True
          return  
        

app.run()