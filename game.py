#game.py

import pygame
import sys
from tilemap import TileMap
from player import Player
from levels import *
from inventory import Inventory
from menu import *
import json
from start_menu import StartMenu  # Import StartMenu

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 720
PLAYER_START_POS = (0, 0)
GRAVITY = 0.5
PLAYER_SPEED = 5
JUMP_SPEED = -14
TELEPORT_COOLDOWN = 2000  # 2 seconds in milliseconds
CAMERA_SPEED = 0.1  # Speed of camera interpolation
RESPAWN_DELAY = 2000  # 2 seconds in milliseconds

class Game:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("THE QUEST FOR THE LOST ARTIFACT")
        # Initialize start menu
        self.start_menu = StartMenu(self.screen)  # Create instance of StartMenu
        self.in_start_menu = True  # Flag to show we're in the start menu
        # Initialize Player
        self.Player = Player()
        self.Player.rect.topleft = PLAYER_START_POS
        # Load and play background music
        pygame.mixer.music.load('assets/Sounds/Chill.ogg')
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1)
        # Initialize TileMap
        self.tile_map = TileMap()

        # Load initial level
        self.current_level = '51aa7c80-4ce0-11ef-b800-db70e6809841'
        self.load_level(self.current_level)

        # Initialize physics and camera
        self.player_velocity_y = 0
        self.on_ground = False
        self.last_teleport_time = 0
        self.camera_x, self.camera_y = 0, 0
        self.message_printed = False
        # Initialize inventory
        slot_types = ['normal', 'head', 'chest', 'gloves', 'shoes', 'ring', 'sword']
        self.slot_images = {
            slot_type: pygame.image.load(f'assets/inventory/{slot_type}_slot.png').convert_alpha()
            for slot_type in slot_types
        }
        self.inventory = Inventory(self.screen, self.slot_images)

        # Inventory toggle
        self.inventory_open = False
        # Track key states
        self.attack_key_pressed = False

        # Respawn tracking
        self.respawning = False
        self.respawn_timer = 0

        # Set up the clock for managing the frame rate
        self.clock = pygame.time.Clock()
        self.running = True
        self.in_menu = False  # Flag to track if we're in the menu
        self.menu = Menu(self.screen, self)  # Initialize the menu
        self.in_settings = False  # Initially not in settings
        self.settings_menu = SettingsMenu(self.screen)  # Initialize SettingsMenu     
           
        self.run()

    def load_level(self, level_iid):
        self.current_level = level_iid
        self.tile_map.load_level(level_files[self.current_level], object_files[self.current_level])
     # Load and scale the background image for the level
        background_image_path = background_Object_images[self.current_level][0]
        level_background_surface = pygame.image.load(background_image_path).convert_alpha()
        self.level_background = pygame.transform.scale(level_background_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.tile_rects = self.tile_map.get_tile_rects()
        self.message_printed = False

        start_point = None
        for entity_type, entities in self.tile_map.objects.items():
            if entity_type == 'Start_point' and entities:
                start_point = entities[0]  # Assuming there's only one start point

        if start_point:
            self.Player.rect.topleft = (start_point['x'], start_point['y'])
        else:
            self.Player.rect.topleft = PLAYER_START_POS
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.cleanup_and_exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    self.inventory_open = not self.inventory_open
                if event.key == pygame.K_ESCAPE:
                    self.in_menu = not self.in_menu  # Toggle menu state
                    print("Menu toggled:", self.in_menu)  # Debug statement
                if event.key == pygame.K_a:  # Attack key press
                    if not self.attack_key_pressed:
                        self.attack_key_pressed = True
                        self.Player.current_action = self.Player.advance_attack_sequence()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:  # Attack key release
                    self.attack_key_pressed = False
    def save_game(self):
        # Create a dictionary with game state data
        game_state = {
            'current_level': self.current_level,
            'player_position': (self.Player.rect.x, self.Player.rect.y),
            # Add other relevant game state data here
        }

        # Save game state to a file using json
        with open('game_save.json', 'w') as save_file:
            json.dump(game_state, save_file)

    def load_game(self):
        # Load game state from file
        with open('game_save.json', 'r') as save_file:
            game_state = json.load(save_file)

        # Set game state variables
        self.current_level = game_state['current_level']
        self.load_level(self.current_level)  # Load the saved level
        # Set player position based on loaded data
        player_x, player_y = game_state['player_position']
        self.Player.rect.x = player_x
        self.Player.rect.y = player_y
    def cleanup_and_exit(self):
        pygame.quit()
        sys.exit()

    def handle_input(self):
        if self.respawning:  # Block input during respawn
            return self.Player.current_action

        keys = pygame.key.get_pressed()
        action = self.Player.current_action  # Start with the current action

        if keys[pygame.K_SPACE] and self.on_ground:
            self.player_velocity_y = JUMP_SPEED
            self.on_ground = False
            action = 'jump'
        elif keys[pygame.K_LEFT]:
            self.Player.rect.x -= PLAYER_SPEED
            if self.on_ground:
                action = 'run'
            self.Player.set_flip(True)
        elif keys[pygame.K_RIGHT]:
            self.Player.rect.x += PLAYER_SPEED
            if self.on_ground:
                action = 'run'
            self.Player.set_flip(False)

        # If attack key is pressed, prioritize the attack action
        if keys[pygame.K_a] and self.attack_key_pressed and action != 'jump':
            action = self.Player.current_action

        return action

    def apply_gravity(self):
        if not self.respawning:  # Block gravity during respawn
            self.player_velocity_y += GRAVITY
            self.Player.rect.y += self.player_velocity_y

    def check_collisions(self, previous_position):
        self.on_ground = False
        for tile_rect in self.tile_rects:
            if self.Player.rect.colliderect(tile_rect):
                if previous_position[1] + self.Player.rect.height <= tile_rect.top:
                    self.Player.rect.bottom = tile_rect.top
                    self.player_velocity_y = 0
                    self.on_ground = True
                    return 'idle' if not any(k for k in pygame.key.get_pressed()) else None
                elif previous_position[1] >= tile_rect.bottom:
                    self.Player.rect.top = tile_rect.bottom
                    self.player_velocity_y = 0
                elif previous_position[0] + self.Player.rect.width <= tile_rect.left:
                    self.Player.rect.right = tile_rect.left
                elif previous_position[0] >= tile_rect.right:
                    self.Player.rect.left = tile_rect.right
        return None

    def handle_teleporters(self):
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:

            for level_teleporter in self.tile_map.level_teleporters:
                if self.Player.rect.colliderect(level_teleporter['rect']) and current_time - self.last_teleport_time > TELEPORT_COOLDOWN:
                    destination = level_teleporter['customFields'].get('destination')
                    if destination:
                        destination_iid = destination.get('entityIid')
                        destination_level_iid = destination.get('levelIid')
                        if destination_level_iid and destination_iid:
                            self.load_level(destination_level_iid)
                            destination_level_teleporter = self.find_level_teleporter_by_iid(destination_iid)
                            if destination_level_teleporter:
                                self.Player.rect.topleft = (destination_level_teleporter['x'], destination_level_teleporter['y'])
                                self.last_teleport_time = current_time
                        else:
                            if not self.message_printed:
                                print("Teleporter has no valid destination specified.")
                                self.message_printed = True
                    else:
                        if not self.message_printed:
                            print("Teleporter destination is null.")
                            self.message_printed = True

    def find_level_teleporter_by_iid(self, iid):
        for level_teleporter in self.tile_map.level_teleporters:
            if level_teleporter['iid'] == iid:
                return level_teleporter
        return None
    
    def handle_interaction(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:  # Using the 'E' key to interact with chests
            player_rect = self.Player.rect
            for chest in self.tile_map.chests:
                if chest.rect.colliderect(player_rect) and not chest.opened:
                    chest.toggle_opened()  # Open the chest only if it is not already opened
                    # Add chest items to the inventory in normal slots
                    for item in chest.swords + chest.coins:
                        free_slot_index = self.find_free_normal_inventory_slot()
                        if free_slot_index is not None:
                            self.inventory.add_item(item, free_slot_index)

    def find_free_normal_inventory_slot(self):
        for i, slot in enumerate(self.inventory.slots):
            if slot.slot_type == 'normal' and slot.item is None:
                return i
        return None

    def update_camera(self):
        # Calculate the maximum boundaries of the level based on tile map dimensions and screen size
        max_x = max(self.tile_map.layers[0]['image'].get_width() - SCREEN_WIDTH, 0)
        max_y = max(self.tile_map.layers[0]['image'].get_height() - SCREEN_HEIGHT, 0)

        # Calculate target camera position
        target_camera_x = max(0, min(self.Player.rect.centerx - SCREEN_WIDTH // 2, max_x))
        target_camera_y = max(0, min(self.Player.rect.centery - SCREEN_HEIGHT // 2, max_y))

        # Interpolate camera movement for smoothness
        self.camera_x += (target_camera_x - self.camera_x) * CAMERA_SPEED
        self.camera_y += (target_camera_y - self.camera_y) * CAMERA_SPEED

    def is_out_of_bounds(self):
        max_x = self.tile_map.layers[0]['image'].get_width()
        max_y = self.tile_map.layers[0]['image'].get_height()
        return (
            self.Player.rect.x < 0 or
            self.Player.rect.right > max_x or
            self.Player.rect.y < 0 or
            self.Player.rect.bottom > max_y
        )

    def start_respawn(self):
        self.respawn_timer = pygame.time.get_ticks() + RESPAWN_DELAY
        self.respawning = True

    def respawn_at_spawn_point(self):
        # Find the first spawn point and respawn the player there
        if self.tile_map.spawn_points:
            spawn_point = self.tile_map.spawn_points[0]  # Assuming only one spawn point exists
            # Respawn at the center of the spawn point image
            self.Player.rect.center = (spawn_point['x'] + spawn_point['width'] // 2,
                                        spawn_point['y'] + spawn_point['height'] // 2)
        else:
            # Default respawn at start position
            self.Player.rect.topleft = PLAYER_START_POS
    def handle_start_menu(self):
        action = self.start_menu.handle_mouse()  # Handle mouse input for start menu
        if action == "start":
            self.in_start_menu = False  # Start the game
        elif action == "quit":
            self.running = False  # Quit the game

    def handle_menu(self):
        if self.in_settings:
            action = self.settings_menu.handle_mouse()
            if action == "back":
                self.in_settings = False  # Go back to in-game menu
            return

        if self.in_menu:
            action = self.menu.handle_mouse()
            if action == "resume":
                self.in_menu = False  # Resume the game
            elif action == "settings":
                self.in_settings = True  # Enter settings menu
            elif action == "quit":
                self.running = False

    def run(self):
        while self.running:
            self.handle_events()
            if self.in_start_menu:
                self.start_menu.draw()  # Draw the start menu
                pygame.display.flip()
                self.handle_start_menu()  # Handle start menu interactions
            else:
                self.render()  # Game rendering
                if not self.in_menu:
                    self.update_game_logic()  # Update game logic if not in menu
                else:
                    self.menu.draw()  # Draw the in-game menu
                    self.handle_menu()  # Handle menu interactions

    def update_game_logic(self):
        if self.respawning:
            # Check if the respawn timer has elapsed
            if pygame.time.get_ticks() >= self.respawn_timer:
                self.respawn_at_spawn_point()
                self.respawning = False
                self.player_velocity_y = 0  # Reset vertical velocity after respawn
            return  # Skip the rest of the game logic while respawning

        previous_position = self.Player.rect.topleft
        action = self.handle_input()
        self.handle_teleporters()
        self.handle_interaction()  # Handle chest interaction
        self.tile_map.update_enemies()  # Update enemies each frame       

        self.apply_gravity()
        collision_action = self.check_collisions(previous_position)
        action = collision_action if collision_action else action

        if not self.on_ground and self.player_velocity_y > 0:
            action = 'fall'
        elif not self.on_ground and self.player_velocity_y < 0:
            action = 'jump'

        self.Player.update(action, self.clock.get_time() / 1000.0)
        self.update_camera()

       # Check if out of bounds and initiate respawn if necessary
        if self.is_out_of_bounds():
            self.start_respawn()

    def render(self):
        self.screen.blit(self.level_background, (0, 0))
        self.tile_map.draw_layer(self.screen, self.camera_x, self.camera_y)
        self.tile_map.draw_spawn_point(self.screen, self.camera_x, self.camera_y)
        self.tile_map.draw_chests(self.screen, self.camera_x, self.camera_y)  # Draw chests
        self.Player.draw(self.screen, self.Player.rect.x - self.camera_x, self.Player.rect.y - self.camera_y)
        self.tile_map.draw_enemies(self.screen, self.camera_x, self.camera_y)
        self.tile_map.draw_teleporters(self.screen, self.camera_x, self.camera_y)

        # Draw inventory if open
        if self.inventory_open:
            self.inventory.draw()
        # Draw the menu if it is open
        if self.in_settings:
            self.settings_menu.draw()
        elif self.in_menu:
            self.menu.draw()
        pygame.display.flip()
        self.clock.tick(60)
        
if __name__ == "__main__":
    Game()