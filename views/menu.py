import os
import pygame
from models.game import Game  # Adjust the import path as necessary

def main_menu(screen, game_state):
    """Main menu display and handling"""
    bg_image = pygame.image.load("assets/bg_Menu.png").convert()
    font = pygame.font.SysFont("Cinzel", 48)

    buttons = [
        {"label": "Start Game", "action": "start", "rect": pygame.Rect(670, 820, 200, 50)},
        {"label": "Load Game", "action": "load", "rect": pygame.Rect(890, 820, 200, 50)},
        {"label": "Quit", "action": "quit", "rect": pygame.Rect(1110, 820, 200, 50)},
    ]
    
    for button in buttons:
        text_surface = font.render(button["label"], True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(button["rect"].x + button["rect"].width // 2, 
                                                 button["rect"].y + button["rect"].height // 2))
        button["text_surface"] = text_surface
        button["text_rect"] = text_rect

    running = True
    while running:
        screen.blit(bg_image, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        print(f"Button clicked: {button['label']}")
                        if button["action"] == "start":
                            settings_result = settings_menu(screen)
                            return settings_result
                        elif button["action"] == "load":
                            # Return load action instead of handling here
                            return "load"
                        else:
                            return button["action"]

        for button in buttons:
            pygame.draw.rect(screen, (90, 42, 42), button["rect"])
            screen.blit(button["text_surface"], button["text_rect"])

        pygame.display.flip()

def pause_menu(screen, game):
    """
    Affiche le menu de pause.
    Retourne une action basée sur l'entrée utilisateur.
    """
    # Charger l'image d'arrière-plan (optionnelle)
    bg_image = pygame.image.load("assets/bg_Menu2.png").convert_alpha()
    font = pygame.font.SysFont("Cinzel", 48)

    # Définir les boutons
    buttons = [
        {"label": "Resume", "action": "resume", "rect": pygame.Rect(412, 250, 200, 50)},
        {"label": "Save Game", "action": "save", "rect": pygame.Rect(412, 320, 200, 50)},
        {"label": "Load Game", "action": "load", "rect": pygame.Rect(412, 390, 200, 50)},
        {"label": "Main Menu", "action": "main_menu", "rect": pygame.Rect(412, 460, 200, 50)},
        {"label": "Quit", "action": "quit", "rect": pygame.Rect(412, 530, 200, 50)},
    ]
    
    # Pre-calculate text positions and surfaces
    for button in buttons:
        text_surface = font.render(button["label"], True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(button["rect"].x + button["rect"].width // 2, 
                                                 button["rect"].y + button["rect"].height // 2))
        button["text_surface"] = text_surface
        button["text_rect"] = text_rect
        
    # Create the overlay ONCE outside the loop
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # Semi-transparent black (alpha 128)

    running = True
    while running:
        screen.blit(overlay, (0, 0))
        screen.blit(bg_image, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        if button["action"] == "save":
                            save_filename = save_menu(screen)
                            if save_filename:
                                game.save_game(save_filename)
                        elif button["action"] == "load":
                            game_state = load_menu(screen)
                            #return "load" if game_state == "load" else "resume"
                            
                        else:
                            return button["action"]

        for button in buttons:
            pygame.draw.rect(screen, (90, 42, 42), button["rect"])
            screen.blit(button["text_surface"], button["text_rect"])

        pygame.display.flip()

    return "quit"

def settings_menu(screen):
    bg_image = pygame.image.load("assets/parametre.gif").convert()
    
    # Use Cinzel font for medieval/strategy game feel
    font_main_title = pygame.font.SysFont("Cinzel", 80, bold=True)  # Large title
    font_title = pygame.font.SysFont("Cinzel", 60, bold=True)      # Section headers
    font = pygame.font.SysFont("Cinzel", 48)                       # Regular text

    # Alternative fonts if Cinzel is not available
    try:
        font_main_title = pygame.font.Font("assets/fonts/Cinzel-Bold.ttf", 72)
        font_title = pygame.font.Font("assets/fonts/Cinzel-Bold.ttf", 48)
        font = pygame.font.Font("assets/fonts/Cinzel-Regular.ttf", 36)
    except:
        print("Fallback to system fonts")
    
    # Screen dimensions
    SCREEN_WIDTH = screen.get_width()

    # Settings sections
    BUTTON_SPACING = 70

    map_sizes = ["Small", "Medium", "Large"]
    map_types = ["centre_ressources", "ressources_generales"]
    selected_size = 1
    selected_type = 0

    starting_conditions = ["Maigre", "Moyenne", "Marines"]
    selected_condition = 1

    
    # Pre-calculate button data (text surfaces and rects)
    def create_buttons(button_data):
        buttons = []
        for item in button_data:
            text_surface = font.render(item["label"], True, (255, 255, 255))
            # Calculer le rectangle de texte *avant* de le centrer
            text_rect = text_surface.get_rect()
            # Centrer le rectangle de texte *dans* le rectangle du bouton
            text_rect.center = item["rect"].center
            buttons.append({**item, "text_surface": text_surface, "text_rect": text_rect})
        return buttons

    buttons = create_buttons([
        {"label": "Start", "action": "start_game", "rect": pygame.Rect(670, 980, 200, 50)},
        {"label": "Back", "action": "back", "rect": pygame.Rect(890, 1020, 200, 50)}
    ])

    size_buttons = create_buttons([
        {"label": size, "rect": pygame.Rect(600, 530 + i * BUTTON_SPACING, 200, 50)}
        for i, size in enumerate(map_sizes)
    ])

    type_buttons = create_buttons([
        {"label": type_name, "rect": pygame.Rect(530, 800 + i * BUTTON_SPACING, 380, 50)}
        for i, type_name in enumerate(map_types)
    ])

    condition_buttons = create_buttons([
        {"label": cond, "rect": pygame.Rect(1300, 430 + i * BUTTON_SPACING, 200, 50)}
        for i, cond in enumerate(starting_conditions)
    ])

    running = True
    while running:
        screen.blit(bg_image, (0, 0))

        # Draw titles
        main_title = font_main_title.render("SETTINGS", True, (90, 42, 42))
        title_rect = main_title.get_rect(center=(SCREEN_WIDTH // 2 + 30, 197))
        screen.blit(main_title, title_rect)

        title_size = font_title.render("Map Size", True, (90, 42, 42))
        title_type = font_title.render("Resource Distribution", True, (90, 42, 42))
        title_condition = font_title.render("Starting Condition", True, (90, 42, 42))
        screen.blit(title_size, (600, 460))
        screen.blit(title_type, (500, 730))
        screen.blit(title_condition, (1250, 350))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return {"action": "quit"}

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        if button["action"] == "start_game":
                            return {
                                "action": "start",
                                "map_size": map_sizes[selected_size],
                                "map_type": map_types[selected_type],
                                "starting_condition": starting_conditions[selected_condition]
                            }
                        elif button["action"] == "back":
                            return "back"

                for i, size_button in enumerate(size_buttons):
                    if size_button["rect"].collidepoint(event.pos):
                        selected_size = i

                for i, type_button in enumerate(type_buttons):
                    if type_button["rect"].collidepoint(event.pos):
                        selected_type = i

                for i, condition_button in enumerate(condition_buttons):
                    if condition_button["rect"].collidepoint(event.pos):
                        selected_condition = i

        # Draw buttons (using pre-calculated data)
        def draw_buttons(buttons_to_draw, selected_index):
            for i, button in enumerate(buttons_to_draw):
                color = (120, 60, 60) if i == selected_index else (90, 42, 42)
                pygame.draw.rect(screen, color, button["rect"])
                # Blit le texte à sa position calculée
                screen.blit(button["text_surface"], button["text_rect"])
        
        draw_buttons(buttons, -1) #No selection for these buttons
        draw_buttons(size_buttons, selected_size)
        draw_buttons(type_buttons, selected_type)
        draw_buttons(condition_buttons, selected_condition)

        pygame.display.flip()

    return "quit"

def load_menu(screen):
    font = pygame.font.SysFont("Cinzel", 48)
    save_files = [f for f in os.listdir('save_games') if f.endswith('.pkl')]

    buttons = []
    for i, save_file in enumerate(save_files):
        rect = pygame.Rect(670, 200 + i * 60, 200, 50)
        buttons.append({"label": save_file, "action": save_file, "rect": rect})

        back_button = {"label": "Back", "rect": pygame.Rect(790, 570, 200, 50)}

    running = True
    while running:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        return button["action"]
                

        for button in buttons:
            text_surface = font.render(button["label"], True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(button["rect"].x + button["rect"].width // 2, 
                                                      button["rect"].y + button["rect"].height // 2))
            pygame.draw.rect(screen, (90, 42, 42), button["rect"])
            screen.blit(text_surface, text_rect)

        pygame.display.flip()

    return "quit"

def get_save_filename(screen):
    font = pygame.font.SysFont("Cinzel", 48)
    input_box = pygame.Rect(670, 400, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            elif event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill((0, 0, 0))
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.flip()

    return text + '.pkl'

def save_menu(screen):
    font = pygame.font.SysFont("Cinzel", 48)
    input_box = pygame.Rect(670, 400, 400, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    save_button = {"label": "Save", "rect": pygame.Rect(670, 500, 200, 50)}
    cancel_button = {"label": "Cancel", "rect": pygame.Rect(880, 500, 200, 50)}

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive

                if save_button["rect"].collidepoint(event.pos):
                    return text + '.pkl'
                elif cancel_button["rect"].collidepoint(event.pos):
                    return None

            elif event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill((0, 0, 0))
        txt_surface = font.render(text, True, color)
        width = max(400, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)

        # Draw Save and Cancel buttons
        save_text_surface = font.render(save_button["label"], True, (255, 255, 255))
        save_text_rect = save_text_surface.get_rect(center=(save_button["rect"].x + save_button["rect"].width // 2, 
                                                            save_button["rect"].y + save_button["rect"].height // 2))
        pygame.draw.rect(screen, (90, 42, 42), save_button["rect"])
        screen.blit(save_text_surface, save_text_rect)

        cancel_text_surface = font.render(cancel_button["label"], True, (255, 255, 255))
        cancel_text_rect = cancel_text_surface.get_rect(center=(cancel_button["rect"].x + cancel_button["rect"].width // 2, 
                                                                cancel_button["rect"].y + cancel_button["rect"].height // 2))
        pygame.draw.rect(screen, (90, 42, 42), cancel_button["rect"])
        screen.blit(cancel_text_surface, cancel_text_rect)

        pygame.display.flip()

    return text + '.pkl'
