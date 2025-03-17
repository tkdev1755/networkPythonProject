from models.Buildings.building import Building
from models.Resources.resource_type import ResourceType

class Camp(Building):
    def __init__(self, position=(0, 0)):
        super().__init__(name="Camp", build_time=25, hp=200, size=(2, 2), position=position, symbol="C")
        self.offset_x = 30
        self.offset_y = 120
        self.cost = {ResourceType.WOOD: 100}