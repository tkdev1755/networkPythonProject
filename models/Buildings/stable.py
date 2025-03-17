from .building import Building
from models.Resources.resource_type import ResourceType
import time

class Stable(Building):
    def __init__(self, position=(0, 0)):
        super().__init__(name="Stable", build_time=50, hp=500, size=(3, 3), position=position, symbol="S")
        self.offset_x = 75
        self.offset_y = 25
        self.cost = {ResourceType.WOOD: 175}

    def spawn_horseman(self, map, player):
        from models.Units.horseman import Horseman  # Local import to avoid circular import
        if player.resources[ResourceType.FOOD] < 80 or player.resources[ResourceType.GOLD] < 20:
            raise ValueError("Not enough resources to create a Horseman")
        time.sleep(30)  # Simulate 30 seconds spawn time
        spawn_position = self._find_spawn_position(map)
        if spawn_position:
            horseman = Horseman(position=spawn_position)
            map.add_unit(horseman)
            player.add_unit(horseman)
            player.resources[ResourceType.FOOD] -= 80
            player.resources[ResourceType.GOLD] -= 20
        else:
            raise ValueError("No valid spawn position available")

    def _find_spawn_position(self, map):
        for dx in range(-1, self.size[0] + 1):
            for dy in range(-1, self.size[1] + 1):
                x, y = self.position[0] + dx, self.position[1] + dy
                if 0 <= x < map.width and 0 <= y < map.height:
                    tile = map.get_tile(x, y)
                    if tile.occupant is None or isinstance(tile.occupant, list):
                        return (x, y)
        return None