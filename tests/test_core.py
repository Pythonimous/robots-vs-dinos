import os
import unittest

from robodino.core.grid import Grid, Tile
from robodino.core.characters import Dino, Robot


class GridTestCase(unittest.TestCase):
    """ Tests for grid """

    def setUp(self):
        self.grid = Grid(10, 10)
        empty_path = os.path.join(os.path.dirname(__file__),
                                  "test_files/test.grid.empty.txt")
        with open(empty_path, 'r') as g:
            self.grid_empty = g.read()

        self.tile_00 = self.grid.tile(0, 0)
        self.tile_42 = self.grid.tile(4, 2)

        self.tile_00_neighbors = [None, self.grid.tile(1, 0),
                                  None, self.grid.tile(0, 1)]
        self.tile_42_neighbors = [self.grid.tile(3, 2), self.grid.tile(5, 2),
                                  self.grid.tile(4, 1), self.grid.tile(4, 3)]

    def test_grid(self):
        self.assertEqual(self.grid.height(), 10)
        self.assertEqual(self.grid.width(), 10)
        self.assertEqual(self.grid.visualize(), self.grid_empty)
        self.assertIsInstance(self.grid.tile(0, 0), Tile)
        self.assertEqual(str(self.tile_00), "(0, 0) None")
        self.assertListEqual(list(self.tile_00.get_neighbors().values()),
                             self.tile_00_neighbors)
        self.assertListEqual(list(self.tile_42.get_neighbors().values()),
                             self.tile_42_neighbors)


class CharacterTestCase(unittest.TestCase):
    """ Tests for characters """

    def setUp(self):
        self.grid = Grid(10, 10)
        self.dino1 = Dino(0, 5, 5, self.grid, health=2)
        self.dino2 = Dino(1, 2, 2, self.grid, health=1)
        self.dino3 = Dino(2, 3, 3, self.grid)

        self.robo1 = Robot(0, 3, 2, self.grid, facing="DOWN")
        self.robo2 = Robot(1, 4, 4, self.grid, facing="UP")
        self.robo3 = Robot(2, 0, 0, self.grid, facing="LEFT")

        before_path = os.path.join(os.path.dirname(__file__),
                                   "test_files/test.grid.before.txt")
        with open(before_path, 'r') as g:
            self.grid_before = g.read()

        after_path = os.path.join(os.path.dirname(__file__),
                                  "test_files/test.grid.after.txt")
        with open(after_path, 'r') as g:
            self.grid_after = g.read()

    def test_character_statics(self):
        self.assertEqual(str(self.dino1), "Dino.0")
        self.assertEqual(str(self.robo1), "Robot.0.DOWN")
        self.assertEqual(self.grid.visualize(), self.grid_before)

        self.assertIsInstance(self.grid.tile(5, 5).has(), Dino,
                              f"Expected Dino, but has "
                              f"{type(self.grid.tile(5, 5).has())}")
        self.assertIsInstance(self.grid.tile(3, 2).has(), Robot,
                              f"Expected Robot, but has "
                              f"{type(self.grid.tile(3, 2).has())}")

    def test_character_movements(self):
        self.robo1.turn("LEFT")
        self.robo1.attack()
        self.assertIsNone(self.grid.tile(2, 2).has())
        self.assertEqual(self.grid.tile(3, 3).has(), self.dino3)
        self.assertEqual(self.dino3.health(), 1)
        self.assertDictEqual(self.robo1.info(), {"id": "0",
                                                 "coordinates": [3, 2],
                                                 "facing": 'RIGHT'})

        self.robo2.turn("RIGHT")
        self.robo2.turn("RIGHT")
        self.assertEqual(self.robo2.facing(), "DOWN")

        self.robo2.move("FORWARD")
        self.assertEqual(self.grid.tile(4, 5).has(), self.robo2)
        self.assertEqual(self.robo2.coordinates(), [4, 5])

        self.robo2.turn("LEFT")
        response = self.robo2.move("FORWARD")
        self.assertEqual(response, "OCCUPIED")
        self.assertEqual(self.grid.tile(4, 5).has(), self.robo2)
        self.assertEqual(self.robo2.coordinates(), [4, 5])

        self.robo2.turn("RIGHT")
        self.robo2.attack()
        self.robo2.attack()
        self.assertIsNone(self.grid.tile(5, 5).has())

        self.robo3.move("FORWARD")
        self.assertEqual(self.grid.tile(0, 0).has(), self.robo3)

        self.assertEqual(self.grid.visualize(), self.grid_after)
