from models.Buildings.building import Building
from models.Resources.resource_type import ResourceType

class Farm(Building):
    def __init__(self, position=(0, 0)):
        super().__init__(name="Farm", build_time=10, hp=100, size=(2, 2), position=position, walkable=True, symbol="F")
        
        self.offset_x = 62
        self.offset_y = 0
        self.cost = {ResourceType.WOOD: 60}