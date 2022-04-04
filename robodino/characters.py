class _Character(object):
    def __init__(self, x, y, grid):
        """
        assert 0 <= x < grid.width() and 0 <= y < grid.height(), f"({x}, {y}) is out of bounds."
        assert grid.tile(x, y).has() is None, f"Tile ({x}, {y}) is occupied!"
        """
        self._x = x
        self._y = y
        self._grid = grid
        self._grid.place(x, y, self)


class Dinosaur(_Character):

    def __init__(self, x, y, grid, *, health=2):
        self._health = health
        super(Dinosaur, self).__init__(x, y, grid)

    def __str__(self):
        return "Dinosaur"

    def hit(self):
        self._health -= 1
        if self._health == 0:
            self._grid.clear(self._x, self._y)

    def health(self):
        return self._health


class Robot(_Character):

    def __init__(self, x, y, grid, *, face):
        self._facing = face
        super(Robot, self).__init__(x, y, grid)

    def __str__(self):
        return f"Robot.{self._facing}"

    def facing(self):
        return self._facing

    def turn(self, direction):
        direction_change = {
            "U": {"L": "L", "R": "R"},
            "L": {"L": "D", "R": "U"},
            "D": {"L": "R", "R": "L"},
            "R": {"L": "U", "R": "D"}
        }
        self._facing = direction_change[self._facing][direction]

    def move(self, direction):
        coordinate_changes = {
            "U": {"F": (0, -1), "B": (0, 1)},
            "D": {"F": (0, 1), "B": (0, -1)},
            "L": {"F": (-1, 0), "B": (1, 0)},
            "R": {"F": (1, 0), "B": (-1, 0)}
        }
        dx, dy = coordinate_changes[self._facing][direction]
        if not (0 <= self._x + dx < self._grid.width()) or not (0 <= self._y + dy < self._grid.height()):
            return
        self._grid.place(self._x + dx, self._y + dy, self)
        self._grid.clear(self._x, self._y)
        self._x += dx
        self._y += dy

    def attack(self):
        for x, y in [(self._x - 1, self._y),
                     (self._x + 1, self._y),
                     (self._x, self._y - 1),
                     (self._x, self._y + 1)]:
            if isinstance(self._grid.tile(x, y).has(), Dinosaur):
                self._grid.tile(x, y).has().hit()


