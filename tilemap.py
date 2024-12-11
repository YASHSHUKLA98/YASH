import pygame
import csv
import json
from PIL import Image
from Chest import Chest
from enemy import Enemy  # Import the Enemy class

class TileMap:
    def __init__(self):
        self.layers = []
        self.objects = {}
        self.level_teleporters = []
        self.spawn_points = []  # List to store spawn points
        self.chests = []  # List to store Chest objects
        self.background_objects = []  # List to store background objects
        self.background_objects_images = []  # List to store background object images
        self.enemies = []  # List to store enemy objects
        self.solid_tiles = []  # List to store solid tiles (for collisions)

        # Load teleporter GIF frames
        self.teleporter_frames = self.load_gif_frames('level_teleporter.gif')
        self.current_frame = 0
        self.frame_duration = 100  # Duration each frame is displayed in milliseconds
        self.last_frame_time = pygame.time.get_ticks()

        # Load spawn point frames
        self.spawn_point_frames = self.load_sprite_sheet('sp.png', frame_width=32, frame_height=32)
        self.spawn_point_frame = 0
        self.spawn_point_last_frame_time = pygame.time.get_ticks()
        self.spawn_point_frame_duration = 200  # Duration each frame is displayed in milliseconds

    def load_gif_frames(self, gif_path):
        gif = Image.open(gif_path)
        frames = []
        for frame in range(gif.n_frames):
            gif.seek(frame)
            frame_image = gif.convert('RGBA')
            frame_surface = pygame.image.fromstring(frame_image.tobytes(), frame_image.size, frame_image.mode)
            frames.append(frame_surface)
        return frames

    def load_sprite_sheet(self, sheet_path, frame_width, frame_height):
        sheet = pygame.image.load(sheet_path).convert_alpha()
        sheet_width, sheet_height = sheet.get_size()
        frames = []
        for y in range(sheet_height // frame_height):
            for x in range(sheet_width // frame_width):
                frame = sheet.subsurface((x * frame_width, y * frame_height, frame_width, frame_height))
                frames.append(frame)
        return frames

    def load_level(self, layer_files, object_file=None, background_object_files=None):
        # Load layers from CSV and corresponding images
        self.layers = []
        for csv_path, image_path, tile_width, tile_height in layer_files:
            layer = self.load_layer(csv_path, image_path, tile_width, tile_height)
            self.layers.append(layer)

        # Load objects from JSON
        if object_file:
            self.load_objects(object_file)
            
        self.background_objects_images = []
        if background_object_files:
            for image_path in background_object_files:
                image = pygame.image.load(image_path).convert_alpha()
                self.background_objects_images.append(image)
    
    def load_layer(self, csv_path, image_path, tile_width, tile_height):
        tile_image = pygame.image.load(image_path).convert_alpha()
        tile_rects = []
        with open(csv_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for y, row in enumerate(reader):
                for x, tile in enumerate(row):
                    if tile == '1':  # Assuming '1' represents a solid tile
                        tile_rect = pygame.Rect(x * tile_width, y * tile_height, tile_width, tile_height)
                        tile_rects.append(tile_rect)
                        self.solid_tiles.append(tile_rect)  # Store solid tiles for collision detection
        return {'image': tile_image, 'rects': tile_rects, 'tile_width': tile_width, 'tile_height': tile_height}

    def load_objects(self, json_path):
        with open(json_path) as f:
            data = json.load(f)
        self.objects = data.get('entities', {})
        self.level_teleporters = self.objects.get('Level_teleporter', [])        
        self.spawn_points = self.objects.get('Spwanpoint', [])
        self.chests = []  # Reset chests list
        self.enemy_data = self.objects.get('Enemy', [])
        self.enemies = []  # Reset enemies list
        idle_folder_path = 'Enemies/spirit/idle'
        
        for enemy_info in self.enemy_data:
            x = enemy_info['x']
            y = enemy_info['y']
            width = enemy_info['width']
            height = enemy_info['height']
            gold = enemy_info['customFields'].get('Gold', 0)
            exp = enemy_info['customFields'].get('EXP', 0)
            patrol_range = (x - 100, x + 100)
            enemy = Enemy(x, y, width, height, gold, exp, idle_folder_path, scale_factor=0.5,  patrol_range=patrol_range)  # Specify scale factor
            self.enemies.append(enemy)

        # Load chests from JSON
        chest_data = self.objects.get('Chest', [])
        for chest_info in chest_data:
            equipments = chest_info['customFields'].get('Sword', [])
            materials = chest_info['customFields'].get('Coin', [])
            closed_image = pygame.image.load('Chests/opened.png').convert_alpha()
            opened_image = pygame.image.load('Chests/closed.png').convert_alpha()
            is_opened = chest_info.get('is_opened', False)  # Default to closed if not specified
            chest = Chest(chest_info['x'], chest_info['y'], chest_info['width'], chest_info['height'], closed_image, opened_image, equipments, materials)
            self.chests.append(chest)

        for level_teleporter in self.level_teleporters:
            level_teleporter['rect'] = pygame.Rect(level_teleporter['x'], level_teleporter['y'], level_teleporter['width'], level_teleporter['height'])
        
        # Add 'rect' key to each chest for collision detection
        for chest in self.chests:
            chest.rect = pygame.Rect(chest.rect.x, chest.rect.y, chest.rect.width, chest.rect.height)
    def get_solid_tiles(self):
        """Return a list of solid tile rectangles for collision detection."""
        return self.solid_tiles
    def get_tile_rects(self):
        all_rects = []
        for layer in self.layers:
            all_rects.extend(layer['rects'])
        return all_rects

    def draw_layer(self, screen, camera_x, camera_y):
        for layer in self.layers:
            tile_image = layer['image']
            tile_width = layer['tile_width']
            tile_height = layer['tile_height']
            for tile_rect in layer['rects']:
                screen.blit(tile_image, (tile_rect.x - camera_x, tile_rect.y - camera_y), tile_rect)
        
        # Draw background objects images
        for image in self.background_objects_images:
            screen.blit(image, (0 - camera_x, 0 - camera_y))

    def draw_spawn_point(self, screen, camera_x, camera_y):
        # Draw spawn points
        current_time = pygame.time.get_ticks()
        if current_time - self.spawn_point_last_frame_time > self.spawn_point_frame_duration:
            self.spawn_point_frame = (self.spawn_point_frame + 1) % len(self.spawn_point_frames)
            self.spawn_point_last_frame_time = current_time

        for spawn_point in self.spawn_points:
            screen.blit(self.spawn_point_frames[self.spawn_point_frame], (spawn_point['x'] - camera_x, spawn_point['y'] - camera_y))

    def draw_teleporters(self, screen, camera_x, camera_y):
        current_time = pygame.time.get_ticks()
        if (current_time - self.last_frame_time) > self.frame_duration:
            self.current_frame = (self.current_frame + 1) % len(self.teleporter_frames)
            self.last_frame_time = current_time
        for level_teleporter in self.level_teleporters:
            screen.blit(self.teleporter_frames[self.current_frame], (level_teleporter['x'] - camera_x, level_teleporter['y'] - camera_y))
    
    def draw_chests(self, screen, camera_x, camera_y):
        # Drawing chests on the screen
        for chest in self.chests:
            chest.draw(screen, camera_x, camera_y)

    def draw_enemies(self, screen, camera_x, camera_y):
        for enemy in self.enemies:
            enemy.draw(screen, camera_x, camera_y)


    def update_enemies(self):
        for enemy in self.enemies:
            # Example movement logic (move right)
            enemy.move(dx=enemy.speed, tilemap=self)  # Pass the tilemap
            enemy.update()  # Update animations
