from flask_restx import Resource, abort, Namespace, fields
from flask import request, current_app

from .grid_ns import simulation_state, get_simulation_state

from robodino.core.characters import Robot

robot_ns = Namespace('Robot', description='Robot related endpoints')

robot_in = robot_ns.model('BuildRobot', {
    'coordinates': fields.List(fields.Integer, required=True,
                               min_items=2, max_items=2,
                               description='X, Y coordinates'),
    'facing': fields.String(required=True, pattern='(LEFT|RIGHT|UP|DOWN)',
                            description='Direction the robot is facing')
})

robot_out = robot_ns.inherit('GetRobot', robot_in, {
    'id': fields.String(required=True, description='Unique robot id')
})

robot_turn = robot_ns.model('RobotTurn', {
    'direction': fields.String(required=True, pattern='(LEFT|RIGHT)',
                               description='Direction to turn the robot')
})

robot_move = robot_ns.model('RobotMove', {
    'direction': fields.String(required=True, pattern='(FORWARD|BACKWARD)',
                               description='Direction to move the robot')
})


@robot_ns.route('/')
class Robots(Resource):
    @robot_ns.doc('list_robots')
    @robot_ns.marshal_list_with(robot_out)
    def get(self):
        """ Get a list of currently existing robots """
        robots_info = [robot.info()
                       for robot in current_app.config["ROBOTS"].values()]
        return robots_info

    @robot_ns.doc('create_robot')
    @robot_ns.expect(robot_in, code=201)
    @robot_ns.marshal_with(simulation_state)
    def post(self):
        """ Create a robot given its coordinates and the direction it faces """
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
                       f"X should be in [0; {width-1}]. "
                       f"Y should be in [0; {height-1}].")
        if grid.tile(x, y).has():
            abort(409, 'Tile not empty.')

        facing = robot_specs['facing']
        robot = Robot(robot_id, x, y, current_app.config['GRID'],
                      facing=facing)
        current_app.config['ROBOTS'][robot_id] = robot

        return get_simulation_state()


@robot_ns.route('/<robot_id>')
@robot_ns.param('robot_id', 'The robot identifier')
@robot_ns.response(404, 'Robot not found')
class GetRobot(Resource):
    @robot_ns.doc('get_robot')
    @robot_ns.marshal_with(robot_out)
    def get(self, robot_id):
        """ Get the <id> robot info """
        if robot_id in current_app.config["ROBOTS"]:
            return current_app.config["ROBOTS"][robot_id].info()
        else:
            abort(404, message='Robot not found.')


@robot_ns.route('/<robot_id>/turn')
@robot_ns.param('robot_id', 'The robot identifier')
@robot_ns.response(404, 'Robot not found')
class RobotTurn(Resource):
    @robot_ns.doc('robot_turn')
    @robot_ns.expect(robot_turn)
    @robot_ns.marshal_with(simulation_state)
    def post(self, robot_id):
        """ Turn the <id> robot left or right """
        robot_order = request.get_json()
        if robot_id in current_app.config["ROBOTS"]:
            current_app.config["ROBOTS"][robot_id].turn(
                robot_order["direction"]
            )
            return get_simulation_state()
        else:
            abort(404, message='Robot not found.')


@robot_ns.route('/<robot_id>/move')
@robot_ns.param('robot_id', 'The robot identifier')
@robot_ns.response(404, 'Robot not found')
class RobotMove(Resource):
    @robot_ns.doc('robot_move')
    @robot_ns.expect(robot_move)
    @robot_ns.marshal_with(simulation_state)
    def post(self, robot_id):
        """ Move the <id> robot forward or backward """
        robot_order = request.get_json()
        if robot_id in current_app.config["ROBOTS"]:
            response = current_app.config["ROBOTS"][robot_id].move(
                robot_order["direction"]
            )
            if response == "OUT OF BOUNDS":
                abort(416, "Tried to move robot out of bounds.")
            elif response == "OCCUPIED":
                abort(409, "Illegal move: tile not empty")
            else:
                return get_simulation_state()
        else:
            abort(404, message='Robot not found.')


@robot_ns.route('/<robot_id>/attack')
@robot_ns.param('robot_id', 'The robot identifier')
@robot_ns.response(404, 'Robot not found')
class RobotAttack(Resource):
    @robot_ns.doc('robot_attack')
    @robot_ns.marshal_with(simulation_state)
    def get(self, robot_id):
        """ Attack all the dinos adjacent to the <id> robot """
        if robot_id in current_app.config["ROBOTS"]:
            current_app.config["ROBOTS"][robot_id].attack()
            dinos_triage = list(current_app.config["DINOS"].keys())
            for dino_id in dinos_triage:
                if current_app.config["DINOS"][dino_id].health() == 0:
                    del current_app.config["DINOS"][dino_id]
            return get_simulation_state()
        else:
            abort(404, message='Robot not found.')
