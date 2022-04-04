from flask import (
    current_app, request, Blueprint
)
from flask_restx import Api, Resource, fields

from robodino.core.characters import Robot, Dinosaur

blueprint = Blueprint('CharacterBlueprint', __name__)
api = Api(blueprint, description='Character related endpoints')

robot_in = api.model('BuildRobot', {
    'coordinates': fields.List(fields.Integer, required=True, min_items=2, max_items=2,
                               description='Robot x, y coordinates'),
    'facing': fields.String(required=True, pattern='[LRUD]', description='Direction the robot is facing')
})

robot_out = api.inherit('GetRobot', robot_in, {
    'id': fields.String(required=True, description='Unique robot id')
})


@api.route('/robots')
class Robots(Resource):
    @api.doc('list_robots')
    @api.marshal_list_with(robot_out)
    def get(self):
        """ Get a list of currently existing robots """
        return current_app.config['ROBOTS']

    @api.doc('create_robot')
    @api.marshal_with(robot_in, code=201)
    def post(self):
        """ Create a robot given its coordinates and direction it faces """
        grid = current_app.config["GRID"]
        if current_app.config["GRID"] is None:
            return {'error': "You must create a simulation space first!"}, 422
        robot_specs = api.payload
        robot_id = str(len(current_app.config["ROBOTS"]))
        x, y = map(int, robot_specs['coordinates'])
        width = grid.width()
        height = grid.height()

        if not 0 <= x < width or not 0 <= y < height:
            return {'error': f"Tried to create a the robot out of bounds. "
                             f"X should be in [0; {width-1}]. Y should be in [0; {height-1}]."}, 416
        if grid.tile(x, y).has():
            return {'error': 'Tile not empty.'}, 409

        facing = robot_specs['facing']
        robot = Robot(robot_id, x, y, current_app.config['GRID'], facing=facing)
        current_app.config['ROBOTS'][robot_id] = robot.info()


@api.route('/robot')
@api.param('id', 'The robot identifier')
@api.response(404, 'Robot not found')
class Robot(Resource):
    @api.doc('get_robot')
    @api.marshal_with(robot_out)
    def get(self, id):
        """ Fetch a robot given its identifier """
        return current_app.config["ROBOTS"][id]


