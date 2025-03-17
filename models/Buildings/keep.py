from models.Buildings.building import Building
from models.Resources.resource_type import ResourceType
import math

class Keep(Building):
    def __init__(self, position=(0, 0)):
        super().__init__(name="Keep", build_time=80, hp=800, size=(1, 1), position=position, symbol="K")
        self.attack_power = 5
        self.attack_range = 8
        self.cost = {ResourceType.WOOD: 35 , ResourceType.GOLD: 125}

    def attack(self, target):
        if self.hp <= 0 or target.hp <= 0:
            raise ValueError("The keep or the target unit is already dead")
        distance = math.sqrt((self.position[0] - target.position[0]) ** 2 + (self.position[1] - target.position[1]) ** 2)
        if distance > self.attack_range:
            raise ValueError("Target is out of range")
        target.hp -= self.attack_power
        if target.hp < 0:
            target.hp = 0