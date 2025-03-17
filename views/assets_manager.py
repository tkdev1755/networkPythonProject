# assets_manager.py
import os
import pygame
from models.Resources.terrain_type import Terrain_type

class AssetManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AssetManager, cls).__new__(cls, *args, **kwargs)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
            
        # Initialize empty sprite containers regardless of mode
        self.building_sprites = {}
        self.terrain_textures = {}
        self.broken_building_sprites = {}
        self.ui_assets = {}  # Add UI assets dictionary
        self.villager_sprites = {
            'walking': [],
            'standing': [],
            'building': []
        }
        self.archer_sprites = {
            'walking': [],
            'standing': [],
            'attacking': []
        }
        self.horseman_sprites = {
            'walking': [],
             'standing' : [],
              'attacking' : []
        }
        self.swordsman_sprites = {
            'walking' : [],
            'standing' : [],
            'attacking' : []
        }
        self.wood_sprites = {}
        self.gold_sprites = {}
        self.resource_bar_sprite = None # Add resource bar sprite
        
        self.use_terminal_view = False
        # Skip asset loading in terminal mode
        if 'SDL_VIDEODRIVER' in os.environ and os.environ['SDL_VIDEODRIVER'] == 'dummy':
            self.use_terminal_view = True
            self.initialized = True
            return
            
        # Only load assets in GUI mode
        self.load_all_assets()
        self.load_resource_bar_sprite() # Load the resource bar sprite
        self.initialized = True

    def load_all_assets(self):
        self.load_terrain_textures()
        self.load_wood_sprites()
        self.load_gold_sprites()
        self.load_building_sprites()
        self.load_villager_sprites()
        self.load_archer_sprites()
        self.load_horseman_sprites()
        self.load_swordsman_sprites()

    def load_terrain_textures(self):
        self.terrain_textures = {
            Terrain_type.GRASS: pygame.image.load('assets/t_grass.png').convert_alpha(),
            # Add other terrain types here
        }

    def get_terrain_texture(self, terrain_type):
        """Get texture for specified terrain type"""
        if terrain_type not in self.terrain_textures:
            return self.terrain_textures[Terrain_type.GRASS]
        return self.terrain_textures[terrain_type]

    def load_wood_sprites(self):
        """Load wood sprites (tree.png)"""
        try:
            self.wood_sprites['tree'] = pygame.image.load('assets/Resources/tree.png').convert_alpha()
        except pygame.error as e:
            print(f"Error loading wood sprite: assets/tree.png - {e}")

    def load_gold_sprites(self):
        """Load gold sprites (Gold.png) et les redimensionner."""
        try:
            gold_image = pygame.image.load('assets/Resources/Gold.png').convert_alpha()
            gold_image = pygame.transform.scale(gold_image, (gold_image.get_width() // 2, gold_image.get_height() // 2))
            self.gold_sprites['gold'] = gold_image
        except pygame.error as e:
            print(f"Error loading gold sprite: assets/Gold.png - {e}")

    def load_building_sprites(self):
        try:
            self.building_sprites['Town Centre'] = pygame.image.load('assets/Buildings/town_center.png').convert_alpha()
            
            original_farm = pygame.image.load('assets/Buildings/farm.png').convert_alpha()
            scaled_width = int(original_farm.get_width() * 0.8)
            scaled_height = int(original_farm.get_height() * 0.8)
            self.building_sprites['Farm'] = pygame.transform.scale(original_farm, (scaled_width, scaled_height))

            self.building_sprites['House'] = pygame.image.load('assets/Buildings/House.png').convert_alpha()

            self.building_sprites['Camp'] = pygame.image.load('assets/Buildings/castel.png').convert_alpha()

            original_stable = pygame.image.load('assets/Buildings/Stable.png').convert_alpha()
            scaled_width = int(original_stable.get_width() * 1.5)
            scaled_height = int(original_stable.get_height() * 1.5)
            self.building_sprites['Stable'] = pygame.transform.scale(original_stable, (scaled_width, scaled_height))

            original_barracks = pygame.image.load('assets/Buildings/Barracks.png').convert_alpha()
            scaled_width = int(original_barracks.get_width() / 1.45)
            scaled_height = int(original_barracks.get_height() / 1.45)
            self.building_sprites['Barracks'] = pygame.transform.scale(original_barracks, (scaled_width, scaled_height))

            self.building_sprites['Archery Range'] = pygame.image.load('assets/Buildings/Archery_range.png').convert_alpha()
            
        except pygame.error as e:
            print(f"Erreur de chargement des sprites des bâtiments : {e}")  

    def load_villager_sprites(self):
        # Load building sprites
        for i in range(1, 76):  # 1 to 75
            sprite_path = f'assets/Sprites/Villager/FarmingVillager/Build & Repair/Act/Villageract{i:03d}.png'
            try:
                sprite = pygame.image.load(sprite_path).convert_alpha()
                self.villager_sprites['building'].append(sprite)
            except pygame.error as e:
                print(f"Error loading building sprite {i}: {e}")

        # Load walking sprites
        sprite_dir = "assets/Sprites/Villager/Walk"
        for i in range(16, 76):
            sprite_path = os.path.join(sprite_dir, f"Villagerwalk{i:03d}.png")
            try:
                sprite = pygame.image.load(sprite_path).convert_alpha()
                self.villager_sprites['walking'].append(sprite)
            except pygame.error as e:
                print(f"Couldn't load sprite: {sprite_path}")

        # Load standing sprites
        sprite_dir = "assets/Sprites/Villager/Stand"
        for i in range(53, 75):
            sprite_path = os.path.join(sprite_dir, f"Villagerstand{i:03d}.png")
            try:
                sprite = pygame.image.load(sprite_path).convert_alpha()
                self.villager_sprites['standing'].append(sprite)
            except pygame.error as e:
                print(f"Couldn't load sprite: {sprite_path}")
                
    def load_archer_sprites(self):
      # Load walking sprites
        sprite_dir = "assets/Sprites/Archer/Walk"
        for i in range(1, 15):
            sprite_path = os.path.join(sprite_dir, f"Archerwalk{i:03d}.png")
            try:
                sprite = pygame.image.load(sprite_path).convert_alpha()
                self.archer_sprites['walking'].append(sprite)
            except pygame.error as e:
                print(f"Couldn't load sprite: {sprite_path}")

        # Load standing sprites
        sprite_dir = "assets/Sprites/Archer/Stand"
        for i in range(11, 15):
            sprite_path = os.path.join(sprite_dir, f"Archerstand{i:03d}.png")
            try:
                sprite = pygame.image.load(sprite_path).convert_alpha()
                self.archer_sprites['standing'].append(sprite)
            except pygame.error as e:
                print(f"Couldn't load sprite: {sprite_path}")
                
        # Load attacking sprites
        sprite_dir = "assets/Sprites/Archer/Attack"
        for i in range(1, 25):
            sprite_path = os.path.join(sprite_dir, f"Archerattack{i:03d}.png")
            try:
                sprite = pygame.image.load(sprite_path).convert_alpha()
                self.archer_sprites['attacking'].append(sprite)
            except pygame.error as e:
                print(f"Couldn't load sprite: {sprite_path}")
    
    def load_horseman_sprites(self):
        # Load walking sprites
        sprite_dir = "assets/Sprites/Scout/Walk"
        for i in range(1, 15):
            sprite_path = os.path.join(sprite_dir, f"Scoutwalk{i:03d}.png")
            try:
                sprite = pygame.image.load(sprite_path).convert_alpha()
                self.horseman_sprites['walking'].append(sprite)
            except pygame.error as e:
                print(f"Couldn't load sprite: {sprite_path}")
                
        # Load standing sprites
        sprite_dir = "assets/Sprites/Scout/Stand"
        for i in range(11, 20):
            sprite_path = os.path.join(sprite_dir, f"Scoutstand{i:03d}.png")
            try:
                sprite = pygame.image.load(sprite_path).convert_alpha()
                self.horseman_sprites['standing'].append(sprite)
            except pygame.error as e:
                print(f"Couldn't load sprite: {sprite_path}")
        
        # Load attacking sprites
        sprite_dir = "assets/Sprites/Scout/Attack"
        for i in range(1, 15):
            sprite_path = os.path.join(sprite_dir, f"Scoutattack{i:03d}.png")
            try:
                sprite = pygame.image.load(sprite_path).convert_alpha()
                self.horseman_sprites['attacking'].append(sprite)
            except pygame.error as e:
                print(f"Couldn't load sprite: {sprite_path}")
                
    def load_swordsman_sprites(self):
        # Load walking sprites
        sprite_dir = "assets/Sprites/AxeThrower/Walk"
        for i in range(1, 15):
            sprite_path = os.path.join(sprite_dir, f"Axethrowerwalk{i:03d}.png")
            try:
                sprite = pygame.image.load(sprite_path).convert_alpha()
                scaled_width = int(sprite.get_width() * 1.1)
                scaled_height = int(sprite.get_height() * 1.1)
                scaled_sprite = pygame.transform.scale(sprite, (scaled_width, scaled_height))
                self.swordsman_sprites['walking'].append(scaled_sprite)
            except pygame.error as e:
                print(f"Couldn't load sprite: {sprite_path}")
                
        # Load standing sprites
        sprite_dir = "assets/Sprites/AxeThrower/Stand"
        for i in range(22, 30):
            sprite_path = os.path.join(sprite_dir, f"Axethrowerstand{i:03d}.png")
            try:
                sprite = pygame.image.load(sprite_path).convert_alpha()
                scaled_width = int(sprite.get_width() * 1.1)
                scaled_height = int(sprite.get_height() * 1.1)
                scaled_sprite = pygame.transform.scale(sprite, (scaled_width, scaled_height))
                self.swordsman_sprites['standing'].append(scaled_sprite)
            except pygame.error as e:
                print(f"Couldn't load sprite: {sprite_path}")
        
        # Load attacking sprites
        sprite_dir = "assets/Sprites/AxeThrower/Attack"
        for i in range(1, 25):
            sprite_path = os.path.join(sprite_dir, f"Axethrowerattack{i:03d}.png")
            try:
                sprite = pygame.image.load(sprite_path).convert_alpha()
                scaled_width = int(sprite.get_width() * 1.1)
                scaled_height = int(sprite.get_height() * 1.1)
                scaled_sprite = pygame.transform.scale(sprite, (scaled_width, scaled_height))
                self.swordsman_sprites['attacking'].append(scaled_sprite)
            except pygame.error as e:
                print(f"Couldn't load sprite: {sprite_path}")

    def get_villager_sprites(self, animation_type):
        return self.villager_sprites.get(animation_type, [])
    
    def get_archer_sprites(self, animation_type):
        return self.archer_sprites.get(animation_type, [])
    
    def get_horseman_sprites(self, animation_type):
        return self.horseman_sprites.get(animation_type, [])
    
    def get_swordsman_sprites(self, animation_type):
         return self.swordsman_sprites.get(animation_type,[])

    def load_resource_bar_sprite(self):
        """Load the resource bar sprite."""
        try:
            self.resource_bar_sprite = pygame.image.load('assets/resourcecivpanel.png').convert_alpha()
            #Scale the sprite
            self.resource_bar_sprite = pygame.transform.scale(self.resource_bar_sprite, (600, 70))  # Increase width again
        except pygame.error as e:
            print(f"Error loading resource bar sprite: assets/UI/resource_bar.png - {e}")

    def load_minimap_frame(self):
        """Charge le sprite du cadre de la mini map."""
        return pygame.image.load('assets/resourcecivpanel.png').convert_alpha()

    def apply_tint(self, image, tint_color):
        """Appliquer une teinte de couleur à une image"""
        tinted_image = image.copy()
        # Créer une surface de la même taille avec la couleur de teinte
        tint_surface = pygame.Surface(tinted_image.get_size(), pygame.SRCALPHA)
        tint_surface.fill(tint_color)
        # Appliquer la surface de teinte avec un mode de fusion approprié
        tinted_image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return tinted_image