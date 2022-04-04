class Tile(object):

    def __init__(self, x, y):
        self._x = x
        self._y = y
        self._used_by = None
        self._left_neighbor = None
        self._right_neighbor = None
        self._top_neighbor = None
        self._bottom_neighbor = None

    def __str__(self):
        return f"({self._x}, {self._y}) {str(self._used_by)}"

    def populate(self, grid):
        self._left_neighbor = grid.tile(self._x - 1, self._y)
        self._right_neighbor = grid.tile(self._x + 1, self._y)
        self._top_neighbor = grid.tile(self._x, self._y - 1)
        self._bottom_neighbor = grid.tile(self._x, self._y + 1)

    def place(self, something):
        self._used_by = something

    def clear(self):
        self._used_by = None

    def has(self):
        return self._used_by

    def get_neighbors(self):
        return {"left": self._left_neighbor,
                "right": self._right_neighbor,
                "top": self._top_neighbor,
                "bottom": self._bottom_neighbor}


class Grid(object):

    def __init__(self, width=50, height=50):
        self._width = width
        self._height = height
        self._tiles = {}
        self._fill_grid()

    def _fill_grid(self):
        """ Fill grid with uninitialized tiles """
        for y in range(self._height):
            row = {}
            for x in range(self._width):
                row[x] = Tile(x, y)
            self._tiles[y] = row

        for y in range(self._height):
            for x in range(self._width):
                self._tiles[y][x].populate(self)

    def tile(self, x, y):
        return self._tiles.get(y, {}).get(x, None)

    def width(self):
        return self._width

    def height(self):
        return self._height

    def make_visualization(self):
        rows = list()
        rows.append("#" + self._width * "#" + "#")
        visual_dict = {
            "None": ".",
            "Robot.U": "↑",
            "Robot.D": "↓",
            "Robot.L": "←",
            "Robot.R": "→"
        }
        for y in range(self._height):
            row = "#"
            for tile in self._tiles[y].values():
                at_tile = tile.has()
                if str(at_tile) in visual_dict:  # if nothing or robot
                    row += visual_dict[str(at_tile)]
                else:  # if dino
                    row += str(at_tile.health())
            row += "#"
            rows.append(row)
        rows.append("#" + self._width * "#" + "#")
        return rows

    def visualize(self):
        output = '\n'.join(self.make_visualization())
        return output

    def place(self, x, y, something):
        """
        assert type(something) in {'Robot', 'Dinosaur'},\
            f"Expected one of the following: Robot, Dinosaur, got {type(something)} instead"
        """
        self.tile(x, y).place(something)

    def clear(self, x, y):
        self.tile(x, y).clear()
