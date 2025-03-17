from .resource_type import ResourceType

class Resource:
    def __init__(self, type: ResourceType, quantity: int):
        self.type = type
        self.quantity = quantity

    def __repr__(self):
        return f"Resource(type={self.type}, quantity={self.quantity})"

    def is_gold(self):
        return self.type == ResourceType.GOLD

    def is_wood(self):
        return self.type == ResourceType.WOOD

    def is_food(self):
        return self.type == ResourceType.FOOD
