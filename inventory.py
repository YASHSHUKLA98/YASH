# inventory.py
import pygame

class InventorySlot:
    def __init__(self, x, y, width, height, slot_type='normal'):
        self.rect = pygame.Rect(x, y, width, height)
        self.slot_type = slot_type
        self.item = None
        self.item_padding = 13  # Adjust this value for desired padding

    def draw(self, screen, slot_images):
        if self.slot_type in slot_images:
            screen.blit(slot_images[self.slot_type], (self.rect.x, self.rect.y))
        if self.item:
            # Calculate the position to center the item within the slot
            item_x = self.rect.x + (self.rect.width - self.item.image.get_width() + self.item_padding) // 2
            item_y = self.rect.y + (self.rect.height - self.item.image.get_height() + self.item_padding) // 2
            screen.blit(self.item.image, (item_x, item_y))

    def contains(self, pos):
        return self.rect.collidepoint(pos)

class Inventory:
    def __init__(self, screen, slot_images):
        self.screen = screen
        self.slot_images = slot_images
        self.slots = []
        self.dragged_item = None
        self.dragged_item_index = None
        self.delete_area_rect = pygame.Rect(740, 450, 32, 32)  # Example position and size for delete area
        self.delete_area_image = pygame.transform.scale(pygame.image.load('assets/inventory/delete.png').convert_alpha(), (32, 32))  # Image for delete area
        self.setup_slots()

    def setup_slots(self):
        slot_size = 50
        padding = 10
        screen_width, screen_height = self.screen.get_size()

        # Middle of the screen
        middle_x = screen_width // 2
        middle_y = screen_height // 2

        # Create equipment slots (3x2 grid) at the middle of the screen
        equip_slot_types = ['head', 'chest', 'gloves', 'shoes', 'ring', 'ring', 'sword']
        grid_columns = 2
        grid_rows = 4
        grid_width = grid_columns * (slot_size + padding) - padding
        grid_height = grid_rows * (slot_size + padding) - padding
        start_x = middle_x - grid_width // 2
        start_y = middle_y - grid_height // 2

        for i, slot_type in enumerate(equip_slot_types):
            row = i % grid_rows
            col = i // grid_rows
            x = start_x + col * (slot_size + padding)
            y = start_y + row * (slot_size + padding)
            slot = InventorySlot(x, y, slot_size, slot_size, slot_type=slot_type)
            self.slots.append(slot)

        # Create inventory slots (2 rows x 13 columns) below the equipment slots
        inventory_columns = 13
        inventory_rows = 2
        inventory_start_x = 10  # Bottom left corner of the screen
        inventory_start_y = screen_height - slot_size - padding  # Bottom left corner of the screen

        for row in range(inventory_rows):
            for col in range(inventory_columns):
                x = inventory_start_x + col * (slot_size + padding)
                y = inventory_start_y - row * (slot_size + padding)
                slot = InventorySlot(x, y, slot_size, slot_size)
                self.slots.append(slot)

    def draw(self):
        for slot in self.slots:
            slot.draw(self.screen, self.slot_images)
        if self.dragged_item:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.screen.blit(self.dragged_item.image, (mouse_x - self.dragged_item.image.get_width() // 2, mouse_y - self.dragged_item.image.get_height() // 2))
        # Draw delete area
        self.screen.blit(self.delete_area_image, self.delete_area_rect.topleft)

    def add_item(self, item, slot_index):
        if 0 <= slot_index < len(self.slots):
            self.slots[slot_index].item = item

    def move_item(self, from_index, to_index):
        if 0 <= from_index < len(self.slots) and 0 <= to_index < len(self.slots):
            self.slots[to_index].item, self.slots[from_index].item = self.slots[from_index].item, self.slots[to_index].item

    def remove_item(self, slot_index):
        if 0 <= slot_index < len(self.slots):
            self.slots[slot_index].item = None

    def handle_mouse_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, slot in enumerate(self.slots):
                if slot.contains(event.pos) and slot.item:
                    self.dragged_item = slot.item
                    self.dragged_item_index = i
                    slot.item = None
                    break

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragged_item:
                if self.delete_area_rect.collidepoint(event.pos):
                    # Item is dropped in the delete area
                    self.dragged_item = None  # Delete the item
                else:
                    for i, slot in enumerate(self.slots):
                        if slot.contains(event.pos):
                            if slot.item:
                                # Swap items if the slot already contains an item
                                self.slots[self.dragged_item_index].item, self.slots[i].item = self.slots[i].item, self.dragged_item
                            else:
                                # Place the dragged item into the slot
                                self.slots[i].item = self.dragged_item
                            break
                    else:
                        # If no slot is found, return the item to its original slot
                        self.slots[self.dragged_item_index].item = self.dragged_item

                self.dragged_item = None
                self.dragged_item_index = None
