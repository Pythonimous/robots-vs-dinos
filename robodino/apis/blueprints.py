from flask import (
    current_app, request, Blueprint
)
from flask_restx import Api, Resource, fields, abort

from robodino.core.characters import Robot, Dinosaur
from robodino.core.grid import Grid

blueprint = Blueprint('GameBlueprint', __name__)
api = Api(blueprint, description='Simulation Related Endpoints')


grid_in = api.model('MakeGrid', {
    'width': fields.Integer(required=True, min=1, default=50, description='Grid width'),
    'height': fields.Integer(required=True, min=1, default=50, description='Grid height')
})


character = api.model('GenericCharacter', {
    'coordinates': fields.List(fields.Integer, required=True, min_items=2, max_items=2,
                               description='X, Y coordinates')
})

robot_in = api.inherit('BuildRobot', character, {
    'facing': fields.String(required=True, pattern='(LEFT|RIGHT|UP|DOWN)', description='Direction the robot is facing')
})

robot_out = api.inherit('GetRobot', robot_in, {
    'id': fields.String(required=True, description='Unique robot id')
})

dino_in = api.inherit('BuildDino', character, {
    'health': fields.Integer(required=True, min=1, max=9, default=2, description="Dino's health")
})

dino_out = api.inherit('GetDino', dino_in, {
    'id': fields.String(required=True, description='Unique dino id')
})

simulation_state = api.model('SimulationState', {
    'robots': fields.List(fields.Nested(robot_out), required=True, description='Robots currently in the simulation'),
    'dinos': fields.List(fields.Nested(dino_out), required=True, description='Dinos currently in the simulation')
})


def get_simulation_state():
    robots_info = [robot.info() for robot in current_app.config["ROBOTS"].values()]
    dinos_info = [dino.info() for dino in current_app.config["DINOS"].values()]
    return {"robots": robots_info, 'dinos': dinos_info}


@api.route('/grid')
class SimulationGrid(Resource):
    @api.doc('build_grid')
    @api.expect(grid_in, code=201)
    @api.marshal_with(simulation_state)
    def post(self):
        grid_specs = request.get_json()
        width = grid_specs["width"]
        height = grid_specs["height"]
        current_app.config["GRID"] = Grid(width, height)
        return get_simulation_state()


@api.route('/robots')
class Robots(Resource):
    @api.doc('list_robots')
    @api.marshal_list_with(robot_out)
    def get(self):
        """ Get a list of currently existing robots """
        robots_info = [robot.info() for robot in current_app.config["ROBOTS"].values()]
        return robots_info

    @api.doc('create_robot')
    @api.expect(robot_in, code=201)
    @api.marshal_with(simulation_state)
    def post(self):
        """ Create a robot given its coordinates and direction it faces """
        grid = current_app.config["GRID"]
        if current_app.config["GRID"] is None:
            abort(422, "You must create a simulation space first!")
        robot_specs = request.get_json()
        robot_id = str(len(current_app.config["ROBOTS"]))
        x, y = map(int, robot_specs['coordinates'])
        width = grid.width()
        height = grid.height()

        if not 0 <= x < width or not 0 <= y < height:
            abort(416, f"Tried to create a robot out of bounds. "
                       f"X should be in [0; {width-1}]. Y should be in [0; {height-1}].")
        if grid.tile(x, y).has():
            abort(409, 'Tile not empty.')

        facing = robot_specs['facing']
        robot = Robot(robot_id, x, y, current_app.config['GRID'], facing=facing)
        current_app.config['ROBOTS'][robot_id] = robot

        return get_simulation_state()


@api.route('/robots/<robot_id>')
@api.param('robot_id', 'The robot identifier')
@api.response(404, 'Robot not found')
class GetRobot(Resource):
    @api.doc('get_robot')
    @api.marshal_with(robot_out)
    def get(self, robot_id):
        """ Get a robot given its unique id """
        if robot_id in current_app.config["ROBOTS"]:
            return current_app.config["ROBOTS"][robot_id].info()
        else:
            abort(404, message='Robot not found.')


@api.route('/dinos')
class Dinos(Resource):
    @api.doc('list_dinos')
    @api.marshal_list_with(dino_out)
    def get(self):
        """ Get a list of currently existing dinos """
        dinos_info = [dino.info() for dino in current_app.config["DINOS"].values()]
        return dinos_info

    @api.doc('create_dino')
    @api.expect(dino_in, code=201)
    @api.marshal_with(simulation_state)
    def post(self):
        """ Create a dinosaur given its coordinates and health """
        grid = current_app.config["GRID"]
        if grid is None:
            abort(422, "You must create a simulation space first!")
        dino_specs = request.get_json()
        dino_id = str(len(current_app.config["DINOS"]))
        x, y = map(int, dino_specs['coordinates'])
        width = grid.width()
        height = grid.height()

        if not 0 <= x < width or not 0 <= y < height:
            abort(416, f"Tried to create a dino out of bounds. "
                       f"X should be in [0; {width-1}]. Y should be in [0; {height-1}].")
        if grid.tile(x, y).has():
            abort(409, 'Tile not empty.')

        health = dino_specs['health']
        dinosaur = Dinosaur(dino_id, x, y, current_app.config['GRID'], health=health)
        current_app.config['DINOS'][dino_id] = dinosaur

        return get_simulation_state()


@api.route('/dinos/<dino_id>')
@api.param('dino_id', 'The dino identifier')
@api.response(404, 'Dino not found')
class GetDino(Resource):
    @api.doc('get_dino')
    @api.marshal_with(dino_out)
    def get(self, dino_id):
        """ Get a dino given its unique id """
        if dino_id in current_app.config["DINOS"]:
            return current_app.config["DINOS"][dino_id].info()
        else:
            abort(404, message='Dino not found.')


robot_turn = api.model('RobotTurn', {
    'direction': fields.String(required=True, pattern='(LEFT|RIGHT)', description='Direction to turn the robot')
})

robot_move = api.model('RobotMove', {
    'direction': fields.String(required=True, pattern='(FORWARD|BACKWARD)', description='Direction to move the robot')
})


@api.route('/robots/<robot_id>/turn')
@api.param('robot_id', 'The robot identifier')
@api.response(404, 'Robot not found')
class RobotTurn(Resource):
    @api.doc('robot_turn')
    @api.expect(robot_turn)
    @api.marshal_with(simulation_state)
    def post(self, robot_id):
        robot_order = request.get_json()
        if robot_id in current_app.config["ROBOTS"]:
            current_app.config["ROBOTS"][robot_id].turn(robot_order["direction"])
            return get_simulation_state()
        else:
            abort(404, message='Robot not found.')


@api.route('/robots/<robot_id>/move')
@api.param('robot_id', 'The robot identifier')
@api.response(404, 'Robot not found')
class RobotMove(Resource):
    @api.doc('robot_move')
    @api.expect(robot_move)
    @api.marshal_with(simulation_state)
    def post(self, robot_id):
        robot_order = request.get_json()
        if robot_id in current_app.config["ROBOTS"]:
            response = current_app.config["ROBOTS"][robot_id].move(robot_order["direction"])
            if response == "OUT OF BOUNDS":
                abort(416, "Tried to move robot out of bounds.")
            elif response == "OCCUPIED":
                abort(409, "Illegal move: tile not empty")
            else:
                return get_simulation_state()
        else:
            abort(404, message='Robot not found.')


@api.route('/robots/<robot_id>/attack')
@api.param('robot_id', 'The robot identifier')
@api.response(404, 'Robot not found')
class RobotAttack(Resource):
    @api.doc('robot_attack')
    @api.marshal_with(simulation_state)
    def get(self, robot_id):
        if robot_id in current_app.config["ROBOTS"]:
            current_app.config["ROBOTS"][robot_id].attack()
            dinos_triage = list(current_app.config["DINOS"].keys())
            for dino_id in dinos_triage:
                if current_app.config["DINOS"][dino_id].health() == 0:
                    del current_app.config["DINOS"][dino_id]
            return get_simulation_state()
        else:
            abort(404, message='Robot not found.')