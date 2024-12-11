import pygame
import os

class Player:
    def __init__(self, scale_factor=2):
        self.scale_factor = scale_factor
        self.health = 100  # Set initial health
        self.max_health = 100  # Set maximum health
        self.animations = {
            'idle': self.load_frames('Player/Idle'),
            'run': self.load_frames('Player/Run'),
            'fall': self.load_frames('Player/Fall'),
            'attack1': self.load_frames('Player/Attack'),
            'attack2': self.load_frames('Player/Attack2'),
            'jump': self.load_frames('Player/Jump')
        }
        self.animation_speeds = {
            'idle': 0.1,
            'run': 0.1,
            'fall': 0.1,
            'attack1': 0.05,
            'attack2': 0.05,
            'jump': 0.1
        }
        self.current_action = 'idle'
        self.current_frame = 0
        self.image = self.animations[self.current_action][self.current_frame]
        self.rect = self.image.get_rect()
        self.animation_speed = self.animation_speeds[self.current_action]
        self.time_since_last_frame = 0
        self.flip = False
        self.attack_sequence = 0  # To track the current attack in the sequence

    def load_frames(self, path):
        frames = []
        for file_name in sorted(os.listdir(path)):
            if file_name.endswith('.png'):
                image = pygame.image.load(os.path.join(path, file_name)).convert_alpha()
                width, height = image.get_size()
                image = pygame.transform.scale(image, (int(width * self.scale_factor), int(height * self.scale_factor)))
                frames.append(image)
        return frames

    def update(self, action, dt):
        if action != self.current_action:
            self.current_action = action
            self.current_frame = 0
            self.time_since_last_frame = 0  # Reset the frame timer when action changes
            self.animation_speed = self.animation_speeds[self.current_action]  # Set animation speed based on action

        self.time_since_last_frame += dt

        # Update animation frame if enough time has passed
        if self.time_since_last_frame >= self.animation_speed:
            self.time_since_last_frame = 0
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.current_action])

        # Update the image with the current frame and apply flipping
        frame_image = self.animations[self.current_action][self.current_frame]
        self.image = pygame.transform.flip(frame_image, self.flip, False)

    def draw(self, screen, x, y):
        # Draw the player's image
        screen.blit(self.image, (x, y))
        # Draw the health bar above the player
        self.draw_health_bar(screen, x, y - 20)  # Position the health bar above the player

    def draw_health_bar(self, screen, x, y):
        # Draw the health bar background
        pygame.draw.rect(screen, (255, 0, 0), (x, y, 100, 10))  # Red background
        # Draw the current health
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, (0, 255, 0), (x, y, 100 * health_ratio, 10))  # Green for current health

    def set_flip(self, flip):
        self.flip = flip

    def advance_attack_sequence(self):
        attack_sequences = ['attack1', 'attack2']
        self.attack_sequence = (self.attack_sequence + 1) % len(attack_sequences)
        return attack_sequences[self.attack_sequence]
