# item.py
import pygame
import os

class Item:
    def __init__(self, item_name):
        self.item_name = item_name
        self.image = self.load_image(item_name)

    def load_image(self, item_name):
        # Determine the folder based on item type
        if "sword" in item_name:
            folder = "Swords"
        else:
            folder = "Coin"

        image_path = os.path.join('assets', 'items', folder, f'{item_name}.gif')
        image = pygame.image.load(image_path).convert_alpha()
        return pygame.transform.scale(image, (38, 38))  # Adjust size as needed