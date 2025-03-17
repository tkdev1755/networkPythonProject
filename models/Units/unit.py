from models.Buildings.building import Building
from models.Units.status import Status
import math
from models.Resources.resource_type import ResourceType
from models.Buildings.farm import Farm

class Unit:
    def __init__(self, name, hp, attack, speed, range=1, position=(0, 0), symbol="", offset_x=0, offset_y=0, animation_speed = 5):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.speed = speed
        self.range = range
        self.position = position
        self.symbol = symbol
        self.status = Status.INACTIVE  # Use Status enum
        self.path = []  # Path of the unit
        self.move_progress = 0 # Progress of the unit
        self.move_speed = 0.1 # Speed of move (in % per frame)
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.animation_speed = animation_speed
        self.player_id = None

    def __repr__(self):
        return (f"Unit(name={self.name}, hp={self.hp}, attack={self.attack}, "
                f"speed={self.speed}, range={self.range}, position={self.position}, "
                f"symbol={self.symbol}, status={self.status})")

    def attack_target(self, target, map, enemy_player):
        if self.hp <= 0 or target.hp <= 0:
            raise ValueError("One of the units is already dead")
        if abs(self.position[0] - target.position[0]) > self.range or abs(self.position[1] - target.position[1]) > self.range:
            raise ValueError("Target is out of range")
        target.hp -= self.attack
        if target.hp <= 0:
            target.hp = 0
            if isinstance(target, Unit):
                map.remove_unit(target)
                enemy_player.remove_unit(target)
            elif isinstance(target, Building):
                map.remove_building(target)
                enemy_player.remove_building(target)
        self.status = Status.ATTACKING  # Update status to attacking
        self.path = []  # Stop moving
        if isinstance(target, Unit):
            target.path = []  # Stop moving
            
        print(f"{self.name} attacked {target.name} for {self.attack} damage")
        print(f"{target.name} has {target.hp} HP left")

    @staticmethod
    def heuristic(a, b):
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    @staticmethod
    def neighbors(pos, map):
        x, y = pos
        results = [(x + dx, y + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if dx != 0 or dy != 0]
        results = filter(lambda p: 0 <= p[0] < map.width and 0 <= p[1] < map.height, results)
        return results

    def move(self, map, target_position):
        from queue import PriorityQueue

        start = self.position
        goal = target_position

        frontier = PriorityQueue()
        frontier.put((0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while not frontier.empty():
            _, current = frontier.get()

            if current == goal:
                break

            for next in self.neighbors(current, map):
                tile = map.get_tile(next[0], next[1])
                if tile.is_occupied() and not isinstance(tile.occupant, list) and not tile.occupant.walkable and not isinstance(tile.occupant, Farm):
                    continue
                if tile.has_resource() and tile.resource.type != ResourceType.FOOD:
                    continue
                new_cost = cost_so_far[current] + self.heuristic(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goal, next)
                    frontier.put((priority, next))
                    came_from[next] = current

        if goal is None or goal not in came_from:
            # Find the closest possible position
            closest_tile = None
            min_distance = float('inf')
            for next in self.neighbors(goal, map):
                if next in came_from:
                    distance = self.heuristic(next, goal)
                    if distance < min_distance:
                        min_distance = distance
                        closest_tile = next
            if closest_tile is None:
                print(f"No valid path from {start} to {target_position}")
                self.status = Status.INACTIVE  # Update status to inactive
                return  # No valid path to target position
            goal = closest_tile

        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from[current]
        path.reverse()
        self.path = path  # Store the path in the unit
        self.move_progress = 0 # Initialize progress
        self.status = Status.WALKING  # Update status to walking
        self.map = map # Store the map in the unit

    def move_adjacent_to(self, map, target):
        from queue import PriorityQueue

        start = self.position
        if isinstance(target, Building):
            goal_positions = [(target.position[0] + dx, target.position[1] + dy) for dx in range(-1, target.size[0] + 1) for dy in range(-1, target.size[1] + 1) if dx == -1 or dx == target.size[0] or dy == -1 or dy == target.size[1]]
        else:
            goal_positions = [(target.position[0] + dx, target.position[1] + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if dx != 0 or dy != 0]
        goal_positions = [pos for pos in goal_positions if 0 <= pos[0] < map.width and 0 <= pos[1] < map.height]

        frontier = PriorityQueue()
        frontier.put((0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        goal = None

        while not frontier.empty():
            _, current = frontier.get()

            if current in goal_positions:
                goal = current
                break

            for next in self.neighbors(current, map):
                tile = map.get_tile(next[0], next[1])
                if tile.is_occupied() and not isinstance(tile.occupant, list) and not tile.occupant.walkable:
                    continue
                if tile.has_resource() and tile.resource.type != ResourceType.FOOD:
                    continue
                new_cost = cost_so_far[current] + self.heuristic(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goal_positions[0], next)
                    frontier.put((priority, next))
                    came_from[next] = current

        if goal is None or goal not in came_from:
            # Find the closest possible position
            closest_tile = None
            min_distance = float('inf')
            for next in self.neighbors(goal_positions[0], map):
                if next in came_from:
                    distance = self.heuristic(next, goal_positions[0])
                    if distance < min_distance:
                        min_distance = distance
                        closest_tile = next
            if closest_tile is None:
                print(f"No valid path from {start} to {target.position}")
                self.status = Status.INACTIVE  # Update status to inactive
                return  # No valid path to target position
            goal = closest_tile

        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from[current]
        path.reverse()
        self.path = path  # Store the path in the unit
        self.move_progress = 0 # Initialize progress
        self.status = Status.WALKING  # Update status to walking
        self.map = map # Store the map in the unit

    def update_position(self):
        """Update the position of the unit along its path."""
        if self.status == Status.WALKING and self.path:
            if self.move_progress < 1:
                self.move_progress = min(1, self.move_progress + self.speed / 30)  # Adjust progress based on speed (0.8 tile/s)
            else:
                self.map.remove_unit(self)
                self.position = self.path.pop(0)  # Move to the next position
                self.map.add_unit(self)
                self.move_progress = 0
                if not self.path:
                    self.status = Status.INACTIVE