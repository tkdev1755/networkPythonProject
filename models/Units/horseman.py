from models.Units.unit import Unit

class Horseman(Unit):
    def __init__(self, position=(0, 0)):
        super().__init__(name="Horseman", hp=45, attack=4, speed=1.2, position=position, symbol="h", offset_x=25, offset_y=15, animation_speed=50)