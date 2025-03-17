from models.Resources.map import Map
from models.Player.player import Player
from models.Buildings.towncenter import TownCenter
from models.Buildings.barrack import Barrack
from models.Units.villager import Villager
from models.Buildings.archery_range import ArcheryRange
from models.Buildings.stable import Stable
from models.Resources.resource_type import ResourceType
import pickle
import os
import json

MAP_SIZES = {
    "Small": (120, 120),
    "Medium": (200, 200),
    "Large": (300, 300)
}

STARTING_CONDITIONS = {
    "Maigre": {
        "resources": {ResourceType.FOOD: 50, ResourceType.WOOD: 200, ResourceType.GOLD: 50},
        "buildings": ["TownCenter"],
        "units": ["Villager", "Villager", "Villager"]
    },
    "Moyenne": {
        "resources": {ResourceType.FOOD: 2000, ResourceType.WOOD: 2000, ResourceType.GOLD: 2000},
        "buildings": ["TownCenter"],
        "units": ["Villager", "Villager", "Villager"]
    },
    "Marines": {
        "resources": {ResourceType.FOOD: 20000, ResourceType.WOOD: 20000, ResourceType.GOLD: 20000},
        "buildings": [
            "TownCenter",    # Main town center
            "Barrack",       # Barrack near the center
            "ArcheryRange",  # Archery range near the center
            "TownCenter",    # Secondary town center left
            "Barrack",       # Support barrack
            "TownCenter",    # Secondary town center right
            "ArcheryRange",   # Support archery range
            "Stable",        # Stable near the center
            "Stable"         # Support stable
        ],
        "units": ["Villager"] * 15
    }
}

class Game:
    def __init__(self, width, height, starting_condition="Maigre", map_type="default", strategy_player1="economic", strategy_player2="economic"):
        self.map = Map(width, height)
        self.players = []
        self.add_player(Player(1,strategy_player1), starting_condition)
        self.add_player(Player(2,strategy_player2), starting_condition)
        self.map_type = map_type
        self.map.add_resources(self.map_type)

    def add_player(self, player: Player, starting_condition="Maigre"):
        self.players.append(player)
        self._apply_starting_conditions(player, starting_condition)

    def remove_player(self, player: Player):
        self.players.remove(player)

    def _apply_starting_conditions(self, player: Player, condition_name):
        condition = STARTING_CONDITIONS[condition_name]
        for resource, amount in condition["resources"].items():
            player.add_resource(resource, amount)
        
        if player.player_id == 1:
            offset_x, offset_y = 0, 0
        elif player.player_id == 2:
            offset_x, offset_y = self.map.width - 6, self.map.height - 6
            if condition_name == "Marines":
                offset_x, offset_y = self.map.width - 15, self.map.height - 15
        else:
            offset_x, offset_y = 0, 0  # Default to top left if player id is not 1 or 2

        if condition_name in ["Maigre", "Moyenne"]:
            max_width, max_height = 7, 7
        elif condition_name == "Marines":
            max_width, max_height = 15, 15
        else:
            max_width, max_height = self.map.width, self.map.height

        for building_name in condition["buildings"]:
            position = self._find_valid_position(offset_x, offset_y, building_name, max_width, max_height)
            if building_name == "TownCenter":
                building = TownCenter(position)
            elif building_name == "Barrack":
                building = Barrack(position)
            elif building_name == "ArcheryRange":
                building = ArcheryRange(position)
            elif building_name == "Stable":
                building = Stable(position)
            # Add other building types here
            self.map.add_building(building)
            player.add_building(building)
        
        for unit_name in condition["units"]:
            position = self._find_valid_position_for_unit(offset_x, offset_y, max_width, max_height)
            if unit_name == "Villager":
                unit = Villager(position=position)
            # Add other unit types here
            self.map.add_unit(unit)
            player.add_unit(unit)

    def _find_valid_position(self, offset_x, offset_y, name, max_width, max_height):
        size = {"TownCenter": (4, 4), "Barrack": (3, 3), "ArcheryRange": (3, 3), "Stable": (3, 3)}.get(name, (1, 1))
        for dx in range(offset_x, min(offset_x + max_width, self.map.width) - size[0] + 1, size[0] + 1):
            for dy in range(offset_y, min(offset_y + max_height, self.map.height) - size[1] + 1, size[1] + 1):
                if all(self.map.get_tile(dx + j, dy + i).occupant is None and not self.map.get_tile(dx + j, dy + i).has_resource() for i in range(size[1]) for j in range(size[0])):
                    return (dx, dy)
        raise ValueError("No valid position available")

    def _find_valid_position_for_unit(self, offset_x, offset_y, max_width, max_height):
        for dx in range(offset_x, min(offset_x + max_width, self.map.width)):
            for dy in range(offset_y, min(offset_y + max_height, self.map.height)):
                if self.map.get_tile(dx, dy).occupant is None:
                    return (dx, dy)
        raise ValueError("No valid position available")

    def update(self):
        self.map.update()
        for player in self.players:
            for unit in player.units:
                if unit.hp <= 0:
                    player.remove_unit(unit)
            for building in player.buildings:
                if building.hp <= 0:
                    player.remove_building(building)

    def display(self):
        self.map.display()
        for player in self.players:
            print(player)

    def check_game_over(self):
        for player in self.players:
            # Condition 1: Player has no buildings left
            if not player.buildings:
                return True
            # Condition 2: Player has no units and insufficient resources to create new units
            if not player.units and player.resources[ResourceType.FOOD] < 50:
                return True
            # Condition 3: Player's TownCenter is destroyed
            if not any(isinstance(building, TownCenter) for building in player.buildings):
                return True
            # Condition 4: Player's population is zero and no resources to create new units
            if player.population == 0 and player.resources[ResourceType.FOOD] < 50:
                return True
        return False

    def save_game(self, filename):
        os.makedirs('save_games', exist_ok=True)
        filepath = os.path.join('save_games', filename)
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load_game(filename):
        filepath = os.path.join('save_games', filename)
        with open(filepath, 'rb') as f:
            return pickle.load(f)

    def __repr__(self):
        return (f"Game(map={self.map}, players={len(self.players)})")
    
    def to_json(self):
        """Exporte les données du jeu (joueurs, bâtiments, unités) en JSON."""
        game_data = {
            "players": []
        }
        for player in self.players:
            player_data = {
                "player_id": player.player_id,
                "resources": {k.name: v for k, v in player.resources.items()},
                "buildings": [{
                    "name": building.name,
                    "hp": building.hp,
                    "position": building.position
                } for building in player.buildings] if player.buildings else [],
                "units": [{
                    "name": unit.__class__.__name__,
                    "hp": unit.hp,
                    "position": unit.position
                } for unit in player.units] if player.units else []
            }
            game_data["players"].append(player_data)
        return json.dumps(game_data, indent=4)

    def save_state(self, filename): 
      """Sauvegarde l'état du jeu"""
      import pickle
      with open(filename, 'wb') as f:
        pickle.dump(self, f)

    def load_state(self, filename):
      """Charge l'état du jeu"""
      import pickle
      try:
        with open(filename, 'rb') as f:
          loaded_game = pickle.load(f)
          self.__dict__.update(loaded_game.__dict__)
      except FileNotFoundError:
          print("No save file to load")
