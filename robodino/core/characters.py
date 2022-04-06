class _Character(object):
    def __init__(self, id, x, y, grid):
        self._id = str(id)
        self._x = x
        self._y = y
        self._grid = grid
        self._grid.place(x, y, self)

    def coordinates(self):
        """ Return the character's coordinates """
        return [self._x, self._y]


class Dino(_Character):

    def __init__(self, id, x, y, grid, *, health=2):
        self._health = health
        self._max_health = health
        super(Dino, self).__init__(id, x, y, grid)

    def __str__(self):
        return f"Dino.{self._id}"

    def __eq__(self, other):
        return (self.coordinates() == other.coordinates()) and (self.health() == other.health())

    def hit(self):
        """ Reduce the dino's health by 1 """
        self._health -= 1
        if self._health == 0:
            self._grid.clear(self._x, self._y)

    def health(self):
        """ Return the dino's health """
        return self._health

    def info(self):
        """ Return the dino's id, coordinates, and health """
        return {"id": self._id, "coordinates": [self._x, self._y], "health": self.health()}

    def healthbar(self):
        """ Return the dino's healthbar """
        bar_num = round((self._health / self._max_health) * 10)
        return f"[" + '-' * bar_num + ' ' * (10 - bar_num) + "]" + f" {self._health} / {self._max_health}"


class Robot(_Character):

    def __init__(self, id, x, y, grid, *, facing):
        self._facing = facing
        super(Robot, self).__init__(id, x, y, grid)

    def __str__(self):
        return f"Robot.{self._id}.{self._facing}"

    def __eq__(self, other):
        return (self.coordinates() == other.coordinates()) and (self.facing() == other.facing())

    def facing(self):
        """ Return which direction the robot is facing """
        return self._facing

    def turn(self, direction):
        """ Turn the robot in a given direction """
        direction_change = {
            "UP": {"LEFT": "LEFT", "RIGHT": "RIGHT"},
            "LEFT": {"LEFT": "DOWN", "RIGHT": "UP"},
            "DOWN": {"LEFT": "RIGHT", "RIGHT": "LEFT"},
            "RIGHT": {"LEFT": "UP", "RIGHT": "DOWN"}
        }
        self._facing = direction_change[self._facing][direction]

    def move(self, direction):
        """ Move the robot forward or backward """
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
        """ Make the robot attack the adjacent tiles """
        for x, y in [(self._x - 1, self._y),
                     (self._x + 1, self._y),
                     (self._x, self._y - 1),
                     (self._x, self._y + 1)]:
            neighbor = self._grid.tile(x, y)
            if neighbor:
                occupied_by = neighbor.has()
                if isinstance(occupied_by, Dino):
                    occupied_by.hit()

    def info(self):
        """ Return the robot's id, coordinates, and the direction it is curently facing """
        return {"id": self._id, "coordinates": [self._x, self._y], "facing": self._facing}
