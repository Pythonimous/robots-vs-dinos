import os
import unittest

from robodino.grid import Grid, Tile
from robodino.characters import Dinosaur, Robot


class GridTestCase(unittest.TestCase):
    """ Tests for grid """

    def setUp(self):
        self.grid = Grid(10, 10)
        empty_path = os.path.join(os.path.dirname(__file__), "test_files/test.grid.empty.txt")
        with open(empty_path, 'r') as g:
            self.grid_empty = g.read()

        self.tile_00 = self.grid.tile(0, 0)
        self.tile_42 = self.grid.tile(4, 2)

        self.tile_00_neighbors = [None, self.grid.tile(1, 0), None, self.grid.tile(0, 1)]
        self.tile_42_neighbors = [self.grid.tile(3, 2), self.grid.tile(5, 2),
                                  self.grid.tile(4, 1), self.grid.tile(4, 3)]

    def test_grid(self):
        self.assertEqual(self.grid.height(), 10)
        self.assertEqual(self.grid.width(), 10)
        self.assertEqual(self.grid.visualize(), self.grid_empty)
        self.assertIsInstance(self.grid.tile(0, 0), Tile)
        self.assertEqual(str(self.tile_00), "(0, 0) None")
        self.assertListEqual(list(self.tile_00.get_neighbors().values()), self.tile_00_neighbors)
        self.assertListEqual(list(self.tile_42.get_neighbors().values()), self.tile_42_neighbors)


class CharacterTestCase(unittest.TestCase):
    """ Tests for characters """

    def setUp(self):
        self.grid = Grid(10, 10)
        self.dino1 = Dinosaur(5, 5, self.grid)
        self.dino2 = Dinosaur(2, 2, self.grid, health=1)
        self.dino3 = Dinosaur(3, 3, self.grid)

        self.robo1 = Robot(3, 2, self.grid, face="D")
        self.robo2 = Robot(4, 4, self.grid, face="U")
        self.robo3 = Robot(0, 0, self.grid, face="L")

        before_path = os.path.join(os.path.dirname(__file__), "test_files/test.grid.before.txt")
        with open(before_path, 'r') as g:
            self.grid_before = g.read()

        after_path = os.path.join(os.path.dirname(__file__), "test_files/test.grid.after.txt")
        with open(after_path, 'r') as g:
            self.grid_after = g.read()

    def test_characters(self):
        self.assertEqual(str(self.dino1), "Dinosaur")
        self.assertEqual(str(self.robo1), "Robot.D")
        self.assertEqual(self.grid.visualize(), self.grid_before)

        self.assertIsInstance(self.grid.tile(5, 5).has(), Dinosaur,
                              f"Expected Dinosaur, but has {type(self.grid.tile(5, 5).has())}")
        self.assertIsInstance(self.grid.tile(3, 2).has(), Robot,
                              f"Expected Robot, but has {type(self.grid.tile(3,2).has())}")

        self.robo1.turn("L")
        self.robo1.attack()
        self.assertIsNone(self.grid.tile(2, 2).has())
        self.assertEqual(self.grid.tile(3, 3).has(), self.dino3)
        self.assertEqual(self.dino3.health(), 1)

        self.robo2.turn("R")
        self.robo2.turn("R")
        self.robo2.move("F")
        self.robo2.attack()
        self.robo2.attack()
        self.assertIsNone(self.grid.tile(5, 5).has())
        self.assertEqual(self.robo2.facing(), "D")
        self.assertEqual(self.grid.tile(4, 5).has(), self.robo2)

        self.robo3.move("F")
        self.assertEqual(self.grid.tile(0, 0).has(), self.robo3)

        self.assertEqual(self.grid.visualize(), self.grid_after)
