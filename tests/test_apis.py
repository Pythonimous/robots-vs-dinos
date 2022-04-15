import unittest

from robodino import create_app
from robodino.core.grid import Grid


def grid_create(client, width, height):
    return client.post('/grid', json=dict(
        width=width,
        height=height
    ), follow_redirects=True)


def grid_get(client):
    return client.get('/grid', follow_redirects=True)


def robot_create(client, coordinates, facing):
    return client.post('/robots', json=dict(
        coordinates=coordinates,
        facing=facing
    ), follow_redirects=True)


def robot_turn(client, robot_id, direction):
    return client.post(f"/robots/{robot_id}/turn", json=dict(
        direction=direction
    ), follow_redirects=True)


def robot_move(client, robot_id, direction):
    return client.post(f"/robots/{robot_id}/move", json=dict(
        direction=direction
    ), follow_redirects=True)


def robot_attack(client, robot_id):
    return client.get(f"/robots/{robot_id}/attack", follow_redirects=True)


def robot_get(client, robot_id):
    return client.get(f'/robots/{robot_id}', follow_redirects=True)


def robots_get(client):
    return client.get('/robots', follow_redirects=True)


def dino_create(client, coordinates, health):
    return client.post('/dinos', json=dict(
        coordinates=coordinates,
        health=health
    ), follow_redirects=True)


def dino_get(client, dino_id):
    return client.get(f'/dinos/{dino_id}', follow_redirects=True)


def dinos_get(client):
    return client.get('/dinos', follow_redirects=True)


def dino_health(client, dino_id):
    return client.get(f'/dinos/{dino_id}/health', follow_redirects=True)


def dinos_health(client):
    return client.get('/dinos/health', follow_redirects=True)


class PrimitivesTestcase(unittest.TestCase):
    """ Tests for the REST API: grid creation and related errors """

    def setUp(self):
        self.client = create_app('test_primitives').test_client()

    def test_grid_primitives(self):
        response = robot_create(self.client, [0, 0], "RIGHT")
        assert b'You must create a simulation space first!' in response.data
        response = dino_create(self.client, [0, 0], 1)
        assert b'You must create a simulation space first!' in response.data
        response = grid_get(self.client)
        assert b'You must create a simulation space first!' in response.data

        grid_create(self.client, 10, 10)
        self.assertEqual(self.client.application.config["GRID"], Grid(10, 10))


class CharactersTestCase(unittest.TestCase):
    """ Tests for the REST API: character deployment and movements """

    def setUp(self):
        self.client = create_app('test_characters').test_client()
        grid_create(self.client, 10, 10)

        robot_create(self.client, [1, 1], "LEFT")
        robot_create(self.client, [9, 9], "UP")

        dino_create(self.client, [2, 2], health=11)
        dino_create(self.client, [8, 8], health=2)

    def test_robot_statics(self):
        response = robot_create(self.client, [10, 10], "LEFT")
        assert b'Tried to create a robot out of bounds' in response.data

        response = robot_create(self.client, [1, 1], "RIGHT")
        assert b'Tile not empty' in response.data

        response = robot_get(self.client, 3)
        assert b'Robot not found' in response.data

        robot1 = robot_get(self.client, 1).json
        self.assertDictEqual(
            robot1, {"id": "1", "facing": "UP", "coordinates": [9, 9]})

        robots = robots_get(self.client)
        self.assertListEqual(
            robots.json, [
                {"id": "0", "facing": "LEFT", "coordinates": [1, 1]},
                {"id": "1", "facing": "UP", "coordinates": [9, 9]}
            ]
        )

    def test_dino_statics(self):
        response = dino_create(self.client, [10, 10], 2)
        assert b'Tried to create a dino out of bounds' in response.data

        response = dino_create(self.client, [2, 2], 3)
        assert b'Tile not empty' in response.data

        response = dino_get(self.client, 2)
        assert b'Dino not found' in response.data

        dino1 = dino_get(self.client, 1).json
        self.assertDictEqual(
            dino1, {"id": "1", "health": 2, "coordinates": [8, 8]}
        )

        dinos = dinos_get(self.client)
        self.assertListEqual(
            dinos.json,
            [
                {"id": "0", "health": 11, "coordinates": [2, 2]},
                {"id": "1", "health": 2, "coordinates": [8, 8]}
            ])

    def test_movements(self):
        robot_move(self.client, 0, "FORWARD")
        response = robot_move(self.client, 0, "FORWARD")
        assert b'Tried to move robot out of bounds' in response.data

        robot_move(self.client, 0, "BACKWARD")
        robot_turn(self.client, 0, "LEFT")
        robot_move(self.client, 0, "FORWARD")
        robot_attack(self.client, 0)

        response = robot_move(self.client, 2, "FORWARD")
        assert b'Robot not found' in response.data

        robot_attack(self.client, 1)
        response = robot_attack(self.client, 3)
        assert b'Robot not found' in response.data

        dino_create(self.client, [5, 4], health=1)
        robot_create(self.client, [6, 4], "LEFT")
        robot_create(self.client, [7, 4], "DOWN")

        response = robot_move(self.client, 2, "FORWARD")
        assert b'Illegal move: tile not empty' in response.data

        robot_attack(self.client, 2)

        response = robot_turn(self.client, 5, "LEFT")
        assert b'Robot not found' in response.data

        self.assertDictEqual(
            grid_get(self.client).json,
            {"robots": [
                {"id": "0", "facing": "DOWN", "coordinates": [1, 2]},
                {"id": "1", "facing": "UP", "coordinates": [9, 9]},
                {"id": "2", "facing": "LEFT", "coordinates": [6, 4]},
                {"id": "3", "facing": "DOWN", "coordinates": [7, 4]}
            ],
                "dinos": [
                    {"id": "0", "health": 10, "coordinates": [2, 2]},
                    {"id": "1", "health": 2, "coordinates": [8, 8]}
                ]})

        response = dino_health(self.client, 2)
        assert b'Dino not found' in response.data

        self.assertDictEqual(dino_health(self.client, 0).json, {
            "id": "0", "healthbar": "[--------- ] 10 / 11"
        })

        self.assertListEqual(dinos_health(self.client).json, [
            {"id": "0", "healthbar": "[--------- ] 10 / 11"},
            {"id": "1", "healthbar": "[----------] 2 / 2"}
        ])
