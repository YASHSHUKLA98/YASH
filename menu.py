import pygame
class Menu:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game  # Store the reference to the game instance
        self.font = pygame.font.Font(None, 74)
        self.button_font = pygame.font.Font(None, 36)
        self.resume_button = pygame.Rect(500, 200, 200, 50)
        self.settings_button = pygame.Rect(500, 500, 200, 50)
        self.quit_button = pygame.Rect(500, 600, 200, 50)
        self.save_button = pygame.Rect(500, 300, 200, 50)
        self.load_button = pygame.Rect(500, 400, 200, 50)
        self.menu_lable = pygame.Rect(450, 100, 300, 100)
        self.click_sound = pygame.mixer.Sound('assets/Sounds/click.wav')

        # Load button images
        self.resume_image = pygame.image.load('assets/buttons/Resume.png').convert_alpha()
        self.settings_image = pygame.image.load('assets/buttons/Settings.png').convert_alpha()
        self.quit_image = pygame.image.load('assets/buttons/Quit.png').convert_alpha()
        self.save_image = pygame.image.load('assets/buttons/Save.png').convert_alpha()
        self.load_image = pygame.image.load('assets/buttons/Load.png').convert_alpha()
        self.menu_image = pygame.image.load('assets/buttons/Main_Menu.png').convert_alpha()

        # Scale images
        self.resume_image = pygame.transform.scale(self.resume_image, (self.resume_button.width, self.resume_button.height))
        self.settings_image = pygame.transform.scale(self.settings_image, (self.settings_button.width, self.settings_button.height))
        self.quit_image = pygame.transform.scale(self.quit_image, (self.quit_button.width, self.quit_button.height))
        self.save_image = pygame.transform.scale(self.save_image, (self.save_button.width, self.save_button.height))
        self.load_image = pygame.transform.scale(self.load_image, (self.load_button.width, self.load_button.height))
        self.menu_image = pygame.transform.scale(self.menu_image, (self.menu_lable.width, self.menu_lable.height))

        # Save/Load messages
        self.save_message = None
        self.message_timer = 0
        self.should_exit = False  # New flag to exit menu after message is shown

    def draw(self):
        self.screen.fill((0, 0, 0))

        # Draw buttons
        self.screen.blit(self.resume_image, (self.resume_button.x, self.resume_button.y))
        self.screen.blit(self.settings_image, (self.settings_button.x, self.settings_button.y))
        self.screen.blit(self.quit_image, (self.quit_button.x, self.quit_button.y))
        self.screen.blit(self.save_image, (self.save_button.x, self.save_button.y))
        self.screen.blit(self.load_image, (self.load_button.x, self.load_button.y))
        self.screen.blit(self.menu_image, (self.menu_lable.x, self.menu_lable.y))

        # Show save/load message if exists
        if self.save_message:
            if pygame.time.get_ticks() - self.message_timer < 2000:  # Show for 2 seconds
                message_surface = self.button_font.render(self.save_message, True, (255, 255, 255))
                self.screen.blit(message_surface, (500, 100))  # Position the message on the screen
            else:
                self.save_message = None
                self.should_exit = True  # Exit the menu after message is shown

    def handle_mouse(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.resume_button.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            self.click_sound.play()  # Play click sound
            return "resume"
        elif self.settings_button.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            self.game.in_settings = True
            self.click_sound.play()  # Play click sound
            return "settings"  # Enter settings menu
        elif self.quit_button.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            self.click_sound.play()  # Play click sound
            return "quit"
        elif self.save_button.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            self.click_sound.play()  # Play click sounds
            self.game.save_game()  # Call the save game method from Game class
            self.save_message = "Game Saved!"
            self.message_timer = pygame.time.get_ticks()  # Set the current time
        elif self.load_button.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            self.click_sound.play()  # Play click sound
            self.game.load_game()  # Call the load game method from Game class
            self.save_message = "Game Loaded!"
            self.message_timer = pygame.time.get_ticks()
        return None
    

class SettingsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 74)
        self.button_font = pygame.font.Font(None, 36)
        self.audio_settings_button = pygame.Rect(500, 300, 200, 50)  # Audio Settings Button
        self.back_button = pygame.Rect(20, 20, 50, 50)  # Position at top left corner
        self.back_image = pygame.image.load('assets/buttons/back_button.png').convert_alpha()
        self.back_image = pygame.transform.scale(self.back_image, (self.back_button.width, self.back_button.height))
        self.audio_settings_image = pygame.image.load('assets/buttons/Audio.png').convert_alpha()
        self.audio_settings_image = pygame.transform.scale(self.audio_settings_image, (self.audio_settings_button.width, self.audio_settings_button.height))
        self.settings = pygame.Rect(450, 200, 300, 100)
        self.settings_label = pygame.image.load('assets/Buttons/Settings(MM).png').convert_alpha()
        self.settings_label = pygame.transform.scale(self.settings_label, (self.settings.width, self.settings.height))
        self.click_sound = pygame.mixer.Sound('assets/Sounds/click.wav')

        self.audio_settings_menu = AudioSettingsMenu(screen)  # Initialize audio settings menu
        self.in_audio_settings = False  # Track if in audio settings

    def draw(self):
        if self.in_audio_settings:
            self.audio_settings_menu.draw()
        else:
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.settings_label, (self.settings.x, self.settings.y))


            # Draw buttons
            self.screen.blit(self.audio_settings_image, (self.audio_settings_button.x, self.audio_settings_button.y))
            self.screen.blit(self.back_image, (self.back_button.x, self.back_button.y))

    def handle_mouse(self):
        if self.in_audio_settings:
            action = self.audio_settings_menu.handle_mouse()
            if action == "back":
                self.in_audio_settings = False  # Go back to settings menu
        else:
            mouse_pos = pygame.mouse.get_pos()
            if self.audio_settings_button.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                self.click_sound.play()  # Play click sound
                self.in_audio_settings = True  # Enter audio settings menu
            elif self.back_button.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                self.click_sound.play()  # Play click sound
                return "back"
        return None

class AudioSettingsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 74)
        self.button_font = pygame.font.Font(None, 36)
        self.volume_up_button = pygame.Rect(750, 385, 50, 50)
        self.volume_down_button = pygame.Rect(400, 385, 50, 50)
        self.back_button = pygame.Rect(20, 20, 50, 50)
        self.Audio = pygame.Rect(450, 200, 300, 100)
        self.click_sound = pygame.mixer.Sound('assets/Sounds/click.wav')

        self.volume_up_pressed = False
        self.volume_down_pressed = False

        # Volume Control
        self.volume_bars = 5  # Number of bars (each represents 20%)
        self.current_volume = 3  # Default to 60% (3 bars)
        self.volume_percentage = self.current_volume * 20  # Default is 60%
        self.volume_bar_rects = []
        self.bar_width = 40
        self.bar_height = 20
        self.bar_spacing = 10
        
        for i in range(self.volume_bars):
            rect = pygame.Rect(480 + i * (self.bar_width + self.bar_spacing), 400, self.bar_width, self.bar_height)
            self.volume_bar_rects.append(rect)

        # Load button images
        self.volume_up_image = pygame.image.load('assets/buttons/volume_up.png').convert_alpha()
        self.volume_down_image = pygame.image.load('assets/buttons/volume_down.png').convert_alpha()
        self.back_image = pygame.image.load('assets/buttons/back_button.png').convert_alpha()
        self.audio_label = pygame.image.load('assets/Buttons/Audio(MM).png').convert_alpha()

        # Scale images
        self.volume_up_image = pygame.transform.scale(self.volume_up_image, (50, 50))
        self.volume_down_image = pygame.transform.scale(self.volume_down_image, (50, 50))
        self.back_image = pygame.transform.scale(self.back_image, (self.back_button.width, self.back_button.height))
        self.audio_label = pygame.transform.scale(self.audio_label, (self.Audio.width, self.Audio.height))

        # Sync initial volume to 60%
        pygame.mixer.music.set_volume(self.current_volume / self.volume_bars)

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.audio_label, (self.Audio.x, self.Audio.y))


        # Draw buttons
        self.screen.blit(self.volume_up_image, (self.volume_up_button.x, self.volume_up_button.y))
        self.screen.blit(self.volume_down_image, (self.volume_down_button.x, self.volume_down_button.y))
        self.screen.blit(self.back_image, (self.back_button.x, self.back_button.y))

        # Draw Volume Bars (each represents 20%)
        for i, rect in enumerate(self.volume_bar_rects):
            if i < self.current_volume:
                pygame.draw.rect(self.screen, (0, 255, 0), rect)  # Filled for current volume
            else:
                pygame.draw.rect(self.screen, (100, 100, 100), rect)  # Empty for remaining bars

        # Display current volume percentage
        percentage_surface = self.button_font.render(f"Volume: {self.volume_percentage}%", True, (255, 255, 255))
        self.screen.blit(percentage_surface, (500, 500))

    def handle_mouse(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]

        if self.volume_up_button.collidepoint(mouse_pos):
            if mouse_click and not self.volume_up_pressed:  # Only change volume if not pressed
                if self.current_volume < self.volume_bars:
                    self.current_volume += 1  # Increase volume bar
                    self.volume_percentage = self.current_volume * 20  # Update percentage
                    pygame.mixer.music.set_volume(self.current_volume / self.volume_bars)
                self.volume_up_pressed = True
                self.click_sound.play()  # Play click sound
            elif not mouse_click:
                self.volume_up_pressed = False  # Reset when not pressed

        elif self.volume_down_button.collidepoint(mouse_pos):
            if mouse_click and not self.volume_down_pressed:  # Only change volume if not pressed
                if self.current_volume > 0:
                    self.current_volume -= 1  # Decrease volume bar
                    self.volume_percentage = self.current_volume * 20  # Update percentage
                    pygame.mixer.music.set_volume(self.current_volume / self.volume_bars)
                self.volume_down_pressed = True
                self.click_sound.play()  # Play click sound
            elif not mouse_click:
                self.volume_down_pressed = False  # Reset when not pressed

        elif self.back_button.collidepoint(mouse_pos) and mouse_click:
            return "back"

        return None
    
