from models.Units.unit import Unit
import math

class Archer(Unit):
    def __init__(self, position=(0, 0)):
        super().__init__(name="Archer", hp=30, attack=4, speed=1, range=4, position=position, symbol="a", offset_x=30, offset_y=20, animation_speed=6)

    def attack_unit(self, target):
        if self.hp <= 0 or target.hp <= 0:
            raise ValueError("One of the units is already dead")
        distance = math.sqrt((self.position[0] - target.position[0]) ** 2 + (self.position[1] - target.position[1]) ** 2)
        if distance > 2:
            raise ValueError("Target is out of range")
        target.hp -= self.attack
        if target.hp < 0:
            target.hp = 0