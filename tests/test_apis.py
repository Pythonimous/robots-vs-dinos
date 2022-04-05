import unittest

import robodino
from robodino.core.grid import Grid


def create_grid(client, width, height):
    return client.post('/grid', json=dict(
        width=width,
        height=height
    ), follow_redirects=True)


def create_robot(client, coordinates, facing):
    return client.post('/robots', json=dict(
        coordinates=coordinates,
        facing=facing
    ), follow_redirects=True)


def get_robot(client, robot_id):
    return client.get(f'/robots/{robot_id}', follow_redirects=True)


def get_robots(client):
    return client.get('/robots', follow_redirects=True)


def create_dino(client, coordinates, health):
    return client.post('/dinos', json=dict(
        coordinates=coordinates,
        health=health
    ), follow_redirects=True)


def get_dino(client, dino_id):
    return client.get(f'/dinos/{dino_id}', follow_redirects=True)


def get_dinos(client):
    return client.get('/dinos', follow_redirects=True)


class GridTestCase(unittest.TestCase):
    """ Tests for the REST API grid """

    def setUp(self):
        robodino.app.config['TESTING'] = True
        self.client = robodino.app.test_client()

    def test_static_errors(self):
        response = create_robot(self.client, [0, 0], "RIGHT")
        assert b'You must create a simulation space first!' in response.data
        response = create_dino(self.client, [0, 0], 1)
        assert b'You must create a simulation space first!' in response.data
        response = get_robot(self.client, 1)
        assert b'Robot not found' in response.data
        response = get_dino(self.client, 0)
        assert b'Dino not found' in response.data

    def test_statics(self):
        create_grid(self.client, 20, 20)
        self.assertEqual(self.client.application.config["GRID"], Grid(20, 20))

        response = create_robot(self.client, [20, 20], "LEFT")
        assert b'Tried to create a robot out of bounds' in response.data

        create_robot(self.client, [1, 1], "LEFT")
        response = create_robot(self.client, [1, 1], "RIGHT")
        assert b'Tile not empty' in response.data

        create_robot(self.client, [9, 9], "UP")
        robot1 = get_robot(self.client, 1).json
        self.assertDictEqual(robot1, {"id": "1", "facing": "UP", "coordinates": [9, 9]})

        robots = get_robots(self.client)
        self.assertListEqual(robots.json,
                             [{"id": "0", "facing": "LEFT", "coordinates": [1, 1]},
                              {"id": "1", "facing": "UP", "coordinates": [9, 9]}]
                             )

        response = create_dino(self.client, [20, 20], 2)
        assert b'Tried to create a dino out of bounds' in response.data

        create_dino(self.client, [2, 2], 2)
        response = create_dino(self.client, [2, 2], 3)
        assert b'Tile not empty' in response.data

        create_dino(self.client, [8, 8], health=2)
        dino1 = get_dino(self.client, 1).json
        self.assertDictEqual(dino1, {"id": "1", "health": 2, "coordinates": [8, 8]})

        dinos = get_dinos(self.client)
        self.assertListEqual(dinos.json,
                             [{"id": "0", "health": 2, "coordinates": [2, 2]},
                              {"id": "1", "health": 2, "coordinates": [8, 8]}]
                             )

