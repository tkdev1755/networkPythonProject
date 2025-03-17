# views/game_view.py
import pygame
from models.Resources.terrain_type import Terrain_type
from models.Units.status import Status
from models.Units.villager import Villager
from models.Units.unit import Unit
from models.Units.archer import Archer
from models.Units.horseman import Horseman
from models.Units.swordsman import Swordsman
from models.Buildings.building import Building
from models.Player.player import Player
from models.Resources.resource_type import ResourceType  # Import ResourceType
from models.Resources.resource import Resource  # Import Resource

class GameView:
    def __init__(self, screen, tile_size=50, asset_manager=None):
        self.screen = screen
        self.tile_size = tile_size
        self.asset_manager = asset_manager
        self.unit_sprites = {}
        self.building_sprites = {}
        
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 16)  # Ajout d'une police plus petite
        self.decorations = []
        self.decorations_generated = False
        self.sprite_cache = {}
        self.viewport_width = screen.get_width()
        self.viewport_height = screen.get_height()
        self.dirty_rects = []
        
        self.unit_animation_frames = {}  # Store animation frame indexes for all units
        self.animation_speed = 5 # Default animation speed
        self.standing_animation_speed = 22 # Animation speed for standing
        self.animation_tick = 0
        self.unit_animation_ticks = {} # Store animation ticks for every unit
        self.animation_directions = {} # Store animation directions for every unit
        self.unit_offsets = {} # Store offsets for each unit
        
        # Minimap related
        self.minimap_width = 600 # Largeur
        self.minimap_height = 300  # Hauteur (la moitié de la largeur)
        self.minimap_x = self.viewport_width - self.minimap_width - 10  # Position from the right
        self.minimap_y = self.viewport_height - self.minimap_height - 10  # Position from the bottom
        self.minimap_surface = pygame.Surface((self.minimap_width, self.minimap_height), pygame.SRCALPHA)
        self.minimap_update_interval = 10 # update every 10 frames
        self.minimap_frame_counter = 0
        
        self.resource_bar_height = 70  # Height of the resource bar for each player
        self.resource_bar_spacing = 10  # Spacing between resource bars
        self.resource_icon_size = 40
        self.resource_text_offset = 80
        self.resource_offsets = { # Define the offsets of every resources
            ResourceType.FOOD: 150,    # Offset for FOOD from the start of the bar
            ResourceType.WOOD: 300,    # Offset for WOOD from the start of the bar
            ResourceType.GOLD: 450     # Offset for GOLD from the start of the bar
        }  

        self.show_resource_ui = True  # Show the resource UI by default
        self.show_minimap = True # Ajouter cette variable
        self.show_health_bars=True

    def colorize_surface(self, surface, color):
        """Apply color tint to a surface"""
        colorized = surface.copy()
        colorized.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
        return colorized

    def world_to_screen(self, x, y, camera_x, camera_y):
        tile_width = self.tile_size * 2
        tile_height = self.tile_size 
        iso_x = (x - y) * tile_width // 2 - camera_x
        iso_y = (x + y) * tile_height // 2 - camera_y
        return iso_x, iso_y

    def screen_to_world(self, screen_x, screen_y, camera_x, camera_y):
        tile_width = self.tile_size * 2
        tile_height = self.tile_size
        screen_x -= self.viewport_width // 2
        screen_y -= self.viewport_height // 4
        x = ((screen_x + camera_x) // (tile_width // 2) + (screen_y + camera_y) // (tile_height // 2)) // 2
        y = ((screen_y + camera_y) // (tile_height // 2) - (screen_x + camera_x) // (tile_width // 2)) // 2
        return x, y
    
    def render_map(self, carte, camera_x, camera_y):
        base_textures = {
            Terrain_type.GRASS: self.asset_manager.terrain_textures[Terrain_type.GRASS],
        }
        tile_width = self.tile_size * 2
        tile_height = self.tile_size
        textures = {
            terrain: pygame.transform.scale(texture, (tile_width, tile_height))
            for terrain, texture in base_textures.items()
        }
        screen_width, screen_height = self.screen.get_size()
        map_width = len(carte.grid[0])
        map_height = len(carte.grid)
        min_x, min_y = self.screen_to_world(0, 0, camera_x, camera_y)
        max_x, max_y = self.screen_to_world(screen_width, screen_height, camera_x, camera_y)
        min_x, min_y = int(min_x), int(min_y)
        max_x, max_y = int(max_x), int(max_y)
        padding_x = int(screen_width / tile_width)
        padding_y = int(screen_height / tile_height)
        min_x = max(min_x - padding_x, 0)
        min_y = max(min_y - padding_y, 0)
        max_x = min(max_x + padding_x, map_width - 1)
        max_y = min(max_y + padding_y, map_height - 1)

        units_to_render = []  # List to store adjacent units

        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                tile = carte.get_tile(x, y)
                if not tile:
                    continue
                iso_x, iso_y = self.world_to_screen(x, y, camera_x, camera_y)
                terrain_texture = textures.get(tile.terrain_type, textures[Terrain_type.GRASS])
                self.screen.blit(terrain_texture, (iso_x, iso_y))
                
                if tile.has_resource() and not tile.resource.is_food():
                    if tile.resource.is_wood():
                        tree_offset_y = tile_height // 0.47
                        tree_offset_x = tile_width // 2
                        resource_texture = self.asset_manager.wood_sprites['tree']
                        self.screen.blit(resource_texture, (iso_x - tree_offset_x, iso_y - tree_offset_y))
                    elif tile.resource.is_gold():
                        gold_offset_y = -tile_height // 2.8
                        resource_texture = self.asset_manager.gold_sprites['gold']
                        self.screen.blit(resource_texture, (iso_x + 0, iso_y + gold_offset_y))

                elif tile.is_occupied():
                    occupant = tile.occupant
                    if hasattr(occupant, 'size') and hasattr(occupant, 'name'):
                        if (x, y) == (occupant.position[0] + occupant.size[1] - 1, occupant.position[1] + occupant.size[1] - 1):
                            building_sprite = self.asset_manager.building_sprites.get(occupant.name)
                            
                            if building_sprite:
                                iso_bx, iso_by = self.world_to_screen(occupant.position[0], occupant.position[1], camera_x, camera_y)
                                offset_x = occupant.offset_x
                                offset_y = occupant.offset_y
                                if occupant.player_id == 1:
                                    building_sprite = self.colorize_surface(building_sprite, (100, 100, 255, 255))
                                elif occupant.player_id == 2:
                                    building_sprite = self.colorize_surface(building_sprite, (255, 100, 100, 255))
                                self.screen.blit(building_sprite, (iso_bx - offset_x, iso_by - offset_y))
                                
                # Check for adjacent units
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue  # Skip the current tile
                        adj_x, adj_y = x + dx, y + dy
                        if 0 <= adj_x < map_width and 0 <= adj_y < map_height:
                            adj_tile = carte.get_tile(adj_x, adj_y)
                            if adj_tile.occupant and isinstance(adj_tile.occupant, Unit):
                                units_to_render.append(adj_tile.occupant)
                            elif isinstance(adj_tile.occupant, list):
                                for unit in adj_tile.occupant:
                                     if isinstance(unit, Unit):
                                          units_to_render.append(unit)

        self.render_adjacent_units(units_to_render, carte, camera_x, camera_y)


    def render_adjacent_units(self, units_to_render, carte, camera_x, camera_y):
        """Render units that are adjacent to a tile, ensuring they are drawn on top."""
        seen = set()
        for unit in units_to_render:
            if unit not in seen:
               self.render_units(unit, carte, camera_x, camera_y)
               seen.add(unit)

    def render_units(self, unit, carte, camera_x, camera_y):
        """Render any unit on the map."""
        # Use interpolated position for smooth movement
        if unit.status == Status.WALKING and unit.path:
            next_x, next_y = unit.path[0]
            current_x, current_y = unit.position
            interp_x = current_x + (next_x - current_x) * unit.move_progress
            interp_y = current_y + (next_y - current_y) * unit.move_progress
            iso_x, iso_y = self.world_to_screen(interp_x, interp_y, camera_x, camera_y)
        else:
          iso_x, iso_y = self.world_to_screen(unit.position[0], unit.position[1], camera_x, camera_y)

        # Determine animation type based on unit status
        animation_type = 'standing'  # Default animation type
        if unit.status == Status.WALKING:
            animation_type = 'walking'
        elif unit.status == Status.ATTACKING:
            animation_type = 'attacking' if isinstance(unit, Archer) or isinstance(unit, Horseman) or isinstance(unit, Swordsman) else 'building'  # Use "attacking" for archers


        # Get the correct animation frames
        if isinstance(unit, Villager):
            animation_frames = self.asset_manager.get_villager_sprites(animation_type)
        elif isinstance(unit, Archer):
            animation_frames = self.asset_manager.get_archer_sprites(animation_type)
        elif isinstance(unit, Horseman):
             animation_frames = self.asset_manager.get_horseman_sprites(animation_type)
        elif isinstance(unit, Swordsman):
            animation_frames = self.asset_manager.get_swordsman_sprites(animation_type)
        else:
            animation_frames = self.asset_manager.get_villager_sprites("standing")
        
        if animation_frames:
            # Ensure frame index is initialized for this unit
            if unit not in self.unit_animation_frames:
                self.unit_animation_frames[unit] = {animation_type: 0}
            elif animation_type not in self.unit_animation_frames[unit]:
                self.unit_animation_frames[unit][animation_type] = 0

            # Ensure animation tick is initialized for this unit
            if unit not in self.unit_animation_ticks:
                self.unit_animation_ticks[unit] = {animation_type: 0}
            elif animation_type not in self.unit_animation_ticks[unit]:
                 self.unit_animation_ticks[unit][animation_type] = 0

            # Ensure animation direction is initialized for this unit
            if unit not in self.animation_directions:
                 self.animation_directions[unit] = {animation_type: 1}
            elif animation_type not in self.animation_directions[unit]:
                self.animation_directions[unit][animation_type] = 1
            
            # Ensure offset is initialized for this unit
            if unit not in self.unit_offsets:
                self.unit_offsets[unit] = { 'x' : 0, 'y' : 0}  # Default offsets
                if isinstance(unit, Villager):
                     self.unit_offsets[unit]['x'] = unit.offset_x
                     self.unit_offsets[unit]['y'] = unit.offset_y
                elif isinstance(unit, Archer):
                     self.unit_offsets[unit]['x'] = unit.offset_x
                     self.unit_offsets[unit]['y'] = unit.offset_y
                elif isinstance(unit, Horseman):
                      self.unit_offsets[unit]['x'] = unit.offset_x
                      self.unit_offsets[unit]['y'] = unit.offset_y
                elif isinstance(unit, Swordsman):
                      self.unit_offsets[unit]['x'] = unit.offset_x
                      self.unit_offsets[unit]['y'] = unit.offset_y
                # You can add more condition here for other units
            
            
            frame_index = self.unit_animation_frames[unit][animation_type]
            current_frame = animation_frames[frame_index % len(animation_frames)]
            # Apply blue tint if the unit belongs to player 2
            # Draw building sprite
            if unit.player_id == 1:
                current_frame = self.colorize_surface(current_frame, (100, 100, 255, 255))
            elif unit.player_id == 2:
                current_frame = self.colorize_surface(current_frame, (255, 100, 100, 255))
                
            
           
            self.screen.blit(current_frame, (iso_x + self.unit_offsets[unit]['x'], iso_y - current_frame.get_height() // 2 + self.unit_offsets[unit]['y']))

            # Update animation frame for this unit
            animation_speed = self.animation_speed
            if animation_type == 'standing':
                animation_speed = self.standing_animation_speed

            self.unit_animation_ticks[unit][animation_type] += 1
            if self.unit_animation_ticks[unit][animation_type] >= animation_speed:
                self.unit_animation_frames[unit][animation_type] += self.animation_directions[unit][animation_type]
                self.unit_animation_ticks[unit][animation_type] = 0
                if self.unit_animation_frames[unit][animation_type] >= len(animation_frames) - 1:
                    self.animation_directions[unit][animation_type] = -1
                elif self.unit_animation_frames[unit][animation_type] <= 0:
                   self.animation_directions[unit][animation_type] = 1

        if self.show_health_bars:
            self.draw_health_bar(self.screen, unit, iso_x, iso_y)
                
    def draw_health_bar(self, surface, unit, x, y):
        """Draw a health bar proportional to unit's HP with camera zoom"""
        if not self.show_health_bars:
            return
        # Get zoom from camera
        zoom_level = 1.0
        
        # Bar dimensions scaled with zoom
        bar_width = self.tile_size * 0.8 * zoom_level
        bar_height = max(2, self.tile_size * 0.08 * zoom_level)
        y_offset = self.tile_size * 0.2 * zoom_level
        border = max(1, int(zoom_level))
        
        # Calculate position
        pos_x = x + 32 + (self.tile_size * zoom_level ) / 8
        pos_y = y - 1 * y_offset
        
        # Draw black border
        pygame.draw.rect(surface, (0, 20, 0),
                        (pos_x - border, pos_y - border,
                        bar_width + 2*border, bar_height + 2*border))
        
        # Draw red background
        pygame.draw.rect(surface, (200, 0, 0),
                        (pos_x, pos_y, bar_width, bar_height))
        
        # Draw green health remaining - using hp attribute from Unit class
        if unit.hp > 0:  # Unit class uses hp attribute
            health_ratio = unit.hp / unit.hp  # Using initial hp as max health
            pygame.draw.rect(surface, (0, 190, 0),
                            (pos_x, pos_y, bar_width * health_ratio, bar_height))


    def render_game(self, carte, camera_x, camera_y, clock, players):
        self.render_map(carte, camera_x, camera_y)
        fps = clock.get_fps()
        fps_text = self.font.render(f"FPS: {int(fps)}", True, pygame.Color('white'))
        self.screen.blit(fps_text, (10, 10))

        # Render the resource UI
        if  self.show_resource_ui: # condition d'affichage des barres
            self.render_resource_ui(players)        
        if self.show_minimap: # condition pour la minimap
            self.render_minimap(carte, players)
        self.dirty_rects = []


    def _render_minimap_content(self, carte, players):
        """Renders the minimap content onto the minimap_surface."""
        self.minimap_surface.fill((50, 50, 50))  # Clear the minimap surface

        map_width = carte.width
        map_height = carte.height
        scale_x = self.minimap_width / (map_width * self.tile_size * 2) # Scale X for the minimap
        scale_y = self.minimap_height / (map_height * self.tile_size) # Scale Y for the minimap

        # Iterate through the entire map
        for y in range(map_height):
            for x in range(map_width):
                tile = carte.get_tile(x, y)
                if not tile:
                    continue
                
                # Calculate the isometric position for the minimap using the same tile size
                iso_x, iso_y = self.world_to_screen(x, y, 0, 0)
                
                # Apply scaling and translation for mini map
                mini_x = (iso_x * scale_x) + (self.minimap_width / 2)
                mini_y = (iso_y * scale_y)
                
                # Color for terrains
                tile_color = (100, 150, 50) if tile.terrain_type == Terrain_type.GRASS else (100,100,100) # default grass

                # Draw the terrain as a small square
                mini_tile_size = 6 
                pygame.draw.rect(self.minimap_surface, tile_color, (mini_x, mini_y, mini_tile_size, mini_tile_size))

                # Draw buildings (as a rect) and units (as a circle)
                if tile.is_occupied():
                    occupant = tile.occupant
                    if isinstance(occupant, Building):
                         if any(p.player_id == 1 for p in players if occupant in p.buildings): # check player id
                            building_color = (0, 255, 0)
                         elif any(p.player_id == 2 for p in players if occupant in p.buildings):
                            building_color = (255, 0, 0)
                         else:
                            building_color = (200, 200, 200)
                         pygame.draw.rect(self.minimap_surface, building_color, (mini_x, mini_y, 5, 5)) # Taille des buildings
                    elif isinstance(occupant, Unit) or isinstance(occupant, list):
                        unit_color = (0, 0, 255) if any(p.player_id == 1 for p in players if occupant in p.units) else (255, 255, 0) if any(p.player_id == 2 for p in players if occupant in p.units) else (200, 200, 200)
                        pygame.draw.circle(self.minimap_surface, unit_color, (int(mini_x + 3), int(mini_y + 3)), 4) # Dessiner un cercle (point) pour les unités

    
    def render_minimap(self, carte, players):
        """Renders the minimap onto the screen. Updates only periodically."""
        self.minimap_frame_counter += 1
        if self.minimap_frame_counter >= self.minimap_update_interval:
            self._render_minimap_content(carte, players)
            self.minimap_frame_counter = 0

        self.screen.blit(self.minimap_surface, (self.minimap_x, self.minimap_y))
        # Ajustement du cadre pour qu'il soit légèrement plus grand et ne coupe pas la mini map
        frame_thickness = 3
        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            (self.minimap_x - frame_thickness, self.minimap_y - frame_thickness,
             self.minimap_width + 2 * frame_thickness, self.minimap_height + 2 * frame_thickness),
            frame_thickness
        )  # Ajustement du cadre

    def render_resource_ui(self, players):
        """Renders the resource UI for all players."""
        
        # Calculate the starting position of the UI (top right)
        ui_start_x = self.viewport_width - 620  # Adjust this as needed for padding
        ui_start_y = 10  # Adjust this as needed for top padding
        
        for index, player in enumerate(players):
            # Calculate the y position of the resource bar
            resource_bar_y = ui_start_y + index * (self.resource_bar_height * 2 + self.resource_bar_spacing)
            info_bar_y = resource_bar_y + self.resource_bar_height
            
            # Draw resource bar background
            if self.asset_manager.resource_bar_sprite:
                 self.screen.blit(self.asset_manager.resource_bar_sprite, (ui_start_x, resource_bar_y))
                 self.screen.blit(self.asset_manager.resource_bar_sprite, (ui_start_x, info_bar_y))
            else:
                # Fallback if the sprite doesn't exist
                 pygame.draw.rect(self.screen, (50, 20, 20),
                             (ui_start_x, resource_bar_y, 600, self.resource_bar_height))
                 pygame.draw.rect(self.screen, (50, 20, 20),
                             (ui_start_x, info_bar_y, 600, self.resource_bar_height))
            
            # Calculate the positions for resource icons and texts
            
            # Display Player name
            player_text_surface = self.small_font.render(f"Player {index + 1}", True, (0, 0, 255) if player.player_id == 1 else (255, 0, 0))  # Utiliser une police plus petite
            self.screen.blit(player_text_surface, (ui_start_x + 20, resource_bar_y + 20))  # Afficher le texte du joueur

            # Afficher la population
            population_text_surface = self.small_font.render(f"Population: {player.population}/{player.max_population}", True, pygame.Color('white'))
            self.screen.blit(population_text_surface, (ui_start_x + 20, resource_bar_y + 35))  # Afficher la population sous le nom du joueur
            
            resource_types = [ResourceType.FOOD, ResourceType.WOOD, ResourceType.GOLD]  # Order of resources
            for resource_type in resource_types:
                icon_x = ui_start_x + self.resource_offsets.get(resource_type, 0)  # Use offset from dictionary
                text_x = icon_x + self.resource_icon_size - 50  # Offset for text after icon
                icon_y = resource_bar_y + self.resource_bar_height // 2 - self.resource_icon_size // 2  # Center vertically
                
                # Get the resource sprite
                resource_sprite = None
                if resource_type == ResourceType.FOOD:
                    resource_sprite = pygame.transform.scale(pygame.image.load("assets/iconfood.png").convert_alpha(), (self.resource_icon_size, self.resource_icon_size))
                elif resource_type == ResourceType.WOOD:
                    resource_sprite = pygame.transform.scale(pygame.image.load("assets/iconwood.png").convert_alpha(), (self.resource_icon_size, self.resource_icon_size))
                elif resource_type == ResourceType.GOLD:
                    resource_sprite = pygame.transform.scale(pygame.image.load("assets/icongold.png").convert_alpha(), (self.resource_icon_size, self.resource_icon_size))
                
                if resource_sprite:
                     self.screen.blit(resource_sprite, (icon_x, icon_y))  # Display icon

                amount = player.resources.get(resource_type, 0)
                text_surface = self.font.render(str(amount), True, pygame.Color('white'))
                text_rect = text_surface.get_rect(center=(text_x + self.resource_text_offset , resource_bar_y + self.resource_bar_height // 2))
                self.screen.blit(text_surface, text_rect)  # Display resource amount
            
            # === Affichage de la seconde barre (bâtiments et unités) ===
            
            # === Informations sur les bâtiments
            building_counts = {}
            for building in player.buildings:
                 building_name = building.name
                 building_counts[building_name] = building_counts.get(building_name, 0) + 1

            building_text = "Bâtiments : " + ", ".join([f"{name}: {count}" for name, count in building_counts.items()])
            building_surface = self.small_font.render(building_text, True, pygame.Color('white'))  # Utilisation de la petite police
            building_rect = building_surface.get_rect(topleft=(ui_start_x + 20, info_bar_y + 15))
            self.screen.blit(building_surface, building_rect)
            
             # === Informations sur les unités
            unit_counts = {}
            for unit in player.units:
                unit_name = unit.name
                unit_counts[unit_name] = unit_counts.get(unit_name, 0) + 1

            unit_text = "Unités : " + ", ".join([f"{name}: {count}" for name, count in unit_counts.items()])
            unit_surface = self.small_font.render(unit_text, True, pygame.Color('white'))  # Utilisation de la petite police
            unit_rect = unit_surface.get_rect(topleft=(ui_start_x + 20, info_bar_y + 35))
            self.screen.blit(unit_surface, unit_rect)