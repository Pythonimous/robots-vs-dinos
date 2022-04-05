class _Character(object):
    def __init__(self, id, x, y, grid):
        """
        assert 0 <= x < grid.width() and 0 <= y < grid.height(), f"({x}, {y}) is out of bounds."
        assert grid.tile(x, y).has() is None, f"Tile ({x}, {y}) is occupied!"
        """
        self._id = str(id)
        self._x = x
        self._y = y
        self._grid = grid
        self._grid.place(x, y, self)

    def coordinates(self):
        return [self._x, self._y]


class Dinosaur(_Character):

    def __init__(self, id, x, y, grid, *, health=2):
        self._health = health
        super(Dinosaur, self).__init__(id, x, y, grid)

    def __str__(self):
        return f"Dinosaur.{self._id}"

    def __eq__(self, other):
        return (self.coordinates() == other.coordinates()) and (self.health() == other.health())

    def hit(self):
        self._health -= 1
        if self._health == 0:
            self._grid.clear(self._x, self._y)

    def health(self):
        return self._health

    def info(self):
        return {"id": self._id, "coordinates": [self._x, self._y], "health": self.health()}


class Robot(_Character):

    def __init__(self, id, x, y, grid, *, facing):
        self._facing = facing
        super(Robot, self).__init__(id, x, y, grid)

    def __str__(self):
        return f"Robot.{self._id}.{self._facing}"

    def __eq__(self, other):
        return (self.coordinates() == other.coordinates()) and (self.facing() == other.facing())

    def facing(self):
        return self._facing

    def turn(self, direction):
        direction_change = {
            "UP": {"LEFT": "LEFT", "RIGHT": "RIGHT"},
            "LEFT": {"LEFT": "DOWN", "RIGHT": "UP"},
            "DOWN": {"LEFT": "RIGHT", "RIGHT": "LEFT"},
            "RIGHT": {"LEFT": "UP", "RIGHT": "DOWN"}
        }
        self._facing = direction_change[self._facing][direction]

    def move(self, direction):
        which_neighbor = {
            "UP": {"FORWARD": "UP", "BACKWARD": "DOWN"},
            "DOWN": {"FORWARD": "DOWN", "BACKWARD": "UP"},
            "LEFT": {"FORWARD": "LEFT", "BACKWARD": "RIGHT"},
            "RIGHT": {"FORWARD": "RIGHT", "BACKWARD": "LEFT"}
        }
        current_tile = self._grid.tile(self._x, self._y)
        next_neighbor = current_tile.get_neighbors()[which_neighbor[self._facing][direction]]
        if not next_neighbor:
            return "OUT OF BOUNDS"
        if next_neighbor.has():
            return "OCCUPIED"
        current_tile.clear()
        next_neighbor.place(self)
        self._x, self._y = next_neighbor.coordinates()
        return "OK"

    def attack(self):
        for x, y in [(self._x - 1, self._y),
                     (self._x + 1, self._y),
                     (self._x, self._y - 1),
                     (self._x, self._y + 1)]:
            neighbor = self._grid.tile(x, y)
            if neighbor:
                occupied_by = neighbor.has()
                if isinstance(occupied_by, Dinosaur):
                    occupied_by.hit()

    def info(self):
        return {"id": self._id, "coordinates": [self._x, self._y], "facing": self._facing}
