from .resource import Resource
from .terrain_type import Terrain_type

class Tile:
    def __init__(self, position, occupant=None, resource: Resource = None):
        self.position = position
        self.terrain_type = Terrain_type.GRASS
        self.occupant = occupant
        self.resource = resource

    def __repr__(self):
        return f"Tile(position={self.position}, occupant={self.occupant}, resource={self.resource})"

    def is_occupied(self):
        return self.occupant is not None

    def has_resource(self):
        return self.resource is not None