import pygame
import random

class Cloud:
    def __init__(self, image, x, y, speed, direction):
        self.image = image
        self.x = x
        self.y = y
        self.speed = speed
        self.direction = direction

    def update(self, screen_width):
        # Move clouds in the appropriate direction
        if self.direction == "right":
            self.x += self.speed
            if self.x > screen_width:  # Reset when it moves off-screen
                self.x = -self.image.get_width()
        else:  # Moving left
            self.x -= self.speed
            if self.x < -self.image.get_width():  # Reset when it moves off-screen
                self.x = screen_width

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class StartMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 74)
        self.button_font = pygame.font.Font(None, 36)
        self.start_button = pygame.Rect(500, 300, 200, 50)  # Start button rectangle
        self.quit_button = pygame.Rect(500, 400, 200, 50)   # Quit button rectangle
        self.click_sound = pygame.mixer.Sound('assets/Sounds/click.wav')

        # Load button images (optional, or use text for buttons)
        self.start_image = pygame.image.load('assets/buttons/Start.png').convert_alpha()
        self.quit_image = pygame.image.load('assets/buttons/Quit.png').convert_alpha()

        # Scale images to match button size
        self.start_image = pygame.transform.scale(self.start_image, (self.start_button.width, self.start_button.height))
        self.quit_image = pygame.transform.scale(self.quit_image, (self.quit_button.width, self.quit_button.height))

        # Load the background image
        self.background_image = pygame.image.load('assets/sm_img/background.png').convert()
        self.background_image = pygame.transform.scale(self.background_image, (screen.get_width(), screen.get_height()))

        # Load the cloud images
        self.cloud_images = [
            pygame.image.load('assets/sm_img/cloud_1.png').convert_alpha(),
            pygame.image.load('assets/sm_img/cloud_2.png').convert_alpha()  # Assuming you have a second cloud image
        ]

        # Initialize list of clouds
        self.clouds = []
        self.max_clouds = 5  # Limit number of clouds to avoid performance issues

        # Initialize clouds randomly
        for _ in range(self.max_clouds):
            self.add_cloud()

    def add_cloud(self):
        """Add a new cloud with random attributes."""
        cloud_image = random.choice(self.cloud_images)
        direction = random.choice(["left", "right"])
        
        # Randomize initial positions and speed
        y_position = random.randint(0, self.screen.get_height() // 2)  # Clouds appear in the upper half of the screen
        speed = random.uniform(0.5, 2.0)  # Random speed between 0.5 and 2.0
        if direction == "right":
            x_position = -cloud_image.get_width()  # Start off-screen on the left
        else:
            x_position = self.screen.get_width()  # Start off-screen on the right
            cloud_image = pygame.transform.flip(cloud_image, True, False)  # Flip the image for right-to-left movement

        # Add a cloud object to the list
        self.clouds.append(Cloud(cloud_image, x_position, y_position, speed, direction))

    def draw(self):
        # Draw the background image first
        self.screen.fill((0, 0, 0))  # Fill with black or your desired background color

        self.screen.blit(self.background_image, (0, 0))  # Draw the background image

        # Update and draw clouds
        for cloud in self.clouds:
            cloud.update(self.screen.get_width())
            cloud.draw(self.screen)

        # Draw buttons
        self.screen.blit(self.start_image, (self.start_button.x, self.start_button.y))
        self.screen.blit(self.quit_image, (self.quit_button.x, self.quit_button.y))

    def handle_mouse(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.start_button.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            self.click_sound.play()  # Play click sound
            return "start"
        elif self.quit_button.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            self.click_sound.play()  # Play click sound
            return "quit"
        return None
