import pygame

class Trap(pygame.sprite.Sprite):
    def __init__(self, x, y, frames):
        super().__init__()
        self.frames = frames  # list of frames for animation
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.animation_speed = 0.1
        self.animation_counter = 0

    def update(self, player):
        # Animate the trap
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.animation_counter = 0

        # Detect if player steps on the trap
        if self.rect.colliderect(player.rect):
            player.take_damage(10)  # Assuming player has a take_damage method


# Example of loading trap frames (make sure to replace with your actual file paths)
trap_frames = [
    pygame.image.load('Fire1.png'),
    pygame.image.load('Fire2.png'),
    pygame.image.load('Fire3.png')
    # Add more frames as necessary
]

# Example trap positions (you can load these from a JSON file or any data structure)
trap_positions = [
    {"x": 416,"y": 2210,},
    {"x": 1066,"y": 1638,},
]

# Create a sprite group to manage all traps
traps_group = pygame.sprite.Group()

# Create and add traps to the sprite group
for trap_pos in trap_positions:
    trap = Trap(trap_pos['x'], trap_pos['y'], trap_frames)
    traps_group.add(trap)

# Update and draw traps in your main game loop (not included here)
# In your main loop, you'd call traps_group.update(player) and traps_group.draw(screen)
