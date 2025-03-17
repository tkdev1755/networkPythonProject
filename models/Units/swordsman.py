from models.Units.unit import Unit

class Swordsman(Unit):
    def __init__(self, position=(0, 0)):
        super().__init__(name="Swordsman", hp=40, attack=4, speed=0.9, position=position, symbol="s", offset_x=35, offset_y=25)