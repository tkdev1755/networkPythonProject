from .building import Building
from models.Resources.resource_type import ResourceType

class House(Building):
    def __init__(self, position=(0, 0)):
        super().__init__(name="House", build_time=25, hp=200, size=(2, 2), position=position, symbol="H")
        self.offset_x = 30
        self.offset_y = 20
        self.cost = {ResourceType.WOOD: 25}