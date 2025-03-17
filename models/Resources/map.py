from models.Resources.tile import Tile
from models.Resources.resource import Resource, ResourceType
from models.Buildings.building import Building
from models.Buildings.farm import Farm
from models.Units.unit import Unit
import random

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[Tile((x, y)) for x in range(width)] for y in range(height)]

    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        else:
            raise ValueError("Coordinates out of bounds")

    def set_tile(self, x, y, tile):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = tile
        else:
            raise ValueError("Coordinates out of bounds")

    def add_building(self, building: Building):
        if not self._can_place_building(building):
            raise ValueError("Cannot place building at the specified location")
        for i in range(building.size[1]):
            for j in range(building.size[0]):
                self.grid[building.position[1] + i][building.position[0] + j].occupant = building
                if isinstance(building, Farm):
                    self.grid[building.position[1] + i][building.position[0] + j].resource = Resource(ResourceType.FOOD, 300)

    def remove_building(self, building: Building):
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x].occupant == building:
                    self.grid[y][x].occupant = None

    def _can_place_building(self, building: Building):
        if building.position[0] + building.size[0] > self.width or building.position[1] + building.size[1] > self.height:
            return False
        for i in range(building.size[1]):
            for j in range(building.size[0]):
                if self.grid[building.position[1] + i][building.position[0] + j].occupant is not None or self.grid[building.position[1] + i][building.position[0] + j].has_resource():
                    return False
        return True

    def add_unit(self, unit: Unit):
        x, y = unit.position
        if 0 <= x < self.width and 0 <= y < self.height:
            if self.grid[y][x].occupant is None:
                self.grid[y][x].occupant = [unit]
            elif isinstance(self.grid[y][x].occupant, list):
                self.grid[y][x].occupant.append(unit)
            elif isinstance(self.grid[y][x].occupant, Building) and self.grid[y][x].occupant.walkable:
                if not isinstance(self.grid[y][x].occupant, list):
                    self.grid[y][x].occupant = [self.grid[y][x].occupant]
                self.grid[y][x].occupant.append(unit)
            else:
                raise ValueError("Tile is already occupied by a non-walkable building")
        else:
            raise ValueError("Coordinates out of bounds")

    def remove_unit(self, unit: Unit):
        x, y = unit.position
        if 0 <= x < self.width and 0 <= y < self.height:
            if isinstance(self.grid[y][x].occupant, list) and unit in self.grid[y][x].occupant:
                self.grid[y][x].occupant.remove(unit)
                if not self.grid[y][x].occupant:
                    self.grid[y][x].occupant = None
            else:
                raise ValueError("Unit not found at the specified location")
        else:
            raise ValueError("Coordinates out of bounds")

    def update(self):
        for y in range(self.height):
            for x in range(self.width):
                tile = self.grid[y][x]
                if isinstance(tile.occupant, list):
                    for unit in tile.occupant:
                        if unit.position != (x, y):
                            tile.occupant.remove(unit)
                            new_x, new_y = unit.position
                            if self.grid[new_y][new_x].occupant is None:
                                self.grid[new_y][new_x].occupant = [unit]
                            elif isinstance(self.grid[new_y][new_x].occupant, list):
                                self.grid[new_y][new_x].occupant.append(unit)

    def display(self):
        for y in range(self.height):
            for x in range(self.width):
                tile = self.grid[y][x]
                if tile.occupant:
                    if isinstance(tile.occupant, list):
                        print(tile.occupant[0].symbol, end=' ')
                    else:
                        print(tile.occupant.symbol, end=' ')
                elif tile.has_resource():
                    print(tile.resource.type.value, end=' ')
                else:
                    print('.', end=' ')
            print()
    

    def add_resources(self, map_type="default"):
        if map_type == "ressources_generales":
            self._generate_default_resources()
        elif map_type == "centre_ressources":
            self._generate_central_gold_resources()
        else:
            raise ValueError("Unknown map type")

    def _generate_default_resources(self):
        for y in range(self.height):
            for x in range(self.width):
                if random.random() < 0.03:  # 3% chance to place a resource
                    if self.grid[y][x].occupant is None:
                        resource_type = random.choice([ResourceType.WOOD, ResourceType.GOLD])
                        if resource_type == ResourceType.GOLD:
                            self.grid[y][x].resource = Resource(resource_type, 800)
                        else:
                            self.grid[y][x].resource = Resource(resource_type, 100)

    def _generate_central_gold_resources(self):
        center_x, center_y = self.width // 2, self.height // 2
        radius_x = int(self.width * 0.2)
        radius_y = int(self.height * 0.2)
        for y in range(self.height):
            for x in range(self.width):
                if abs(x - center_x) < radius_x and abs(y - center_y) < radius_y:
                    if random.random() < 0.05:  # 30% chance to place gold
                        if self.grid[y][x].occupant is None:
                            self.grid[y][x].resource = Resource(ResourceType.GOLD, 800)
                elif random.random() < 0.02:  # 10% chance to place other resources
                    if self.grid[y][x].occupant is None:
                        self.grid[y][x].resource = Resource(ResourceType.WOOD, 100)
