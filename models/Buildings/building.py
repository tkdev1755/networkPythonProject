class Building:
    def __init__(self, name, build_time, hp, size, position=(0, 0), walkable=False, symbol=""):
        self.name = name
        self.build_time = build_time
        self.hp = hp
        self.max_hp = hp
        self.size = size
        self.position = position
        self.walkable = walkable
        self.symbol = symbol
        self.offset_x = 0  # Offset X par défaut
        self.offset_y = 0  # Offset Y par défaut
        self.player_id = None

    def __repr__(self):
        return (f"Building(name={self.name}, build_time={self.build_time}, hp={self.hp}, "
                f"size={self.size}, position={self.position}, walkable={self.walkable} symbol={self.symbol})")