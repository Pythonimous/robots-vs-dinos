from flask_restx import Resource, abort, Namespace, fields
from flask import request, current_app

from robodino.core.grid import Grid


grid_ns = Namespace('Grid', description='Grid related endpoints')

grid_in = grid_ns.model('MakeGrid', {
    'width': fields.Integer(required=True, min=1, default=50, description='Grid width'),
    'height': fields.Integer(required=True, min=1, default=50, description='Grid height')
})


robot_ns = Namespace('Robot', description='Robot related endpoints')
robot_out = robot_ns.model('GetRobot', {
    'coordinates': fields.List(fields.Integer, required=True, min_items=2, max_items=2,
                               description='X, Y coordinates'),
    'facing': fields.String(required=True, pattern='(LEFT|RIGHT|UP|DOWN)', description='Direction the robot is facing'),
    'id': fields.String(required=True, description='Unique robot id')
})

dino_ns = Namespace('Dino', description='Dino related endpoints')
dino_out = dino_ns.model('GetDino', {
    'coordinates': fields.List(fields.Integer, required=True, min_items=2, max_items=2,
                               description='X, Y coordinates'),
    'health': fields.Integer(required=True, min=1, default=2, description="Dino's health"),
    'id': fields.String(required=True, description='Unique dino id')
})

simulation_state = grid_ns.model('SimulationState', {
    'robots': fields.List(fields.Nested(robot_out), required=True, description='Robots currently in the simulation'),
    'dinos': fields.List(fields.Nested(dino_out), required=True, description='Dinos currently in the simulation')
})


def get_simulation_state():
    robots_info = [robot.info() for robot in current_app.config["ROBOTS"].values()]
    dinos_info = [dino.info() for dino in current_app.config["DINOS"].values()]
    return {"robots": robots_info, 'dinos': dinos_info}


@grid_ns.route('/')
class SimulationGrid(Resource):
    @grid_ns.doc('build_grid')
    @grid_ns.expect(grid_in, code=201)
    @grid_ns.marshal_with(simulation_state)
    def post(self):
        """ Create grid given its width and height """
        grid_specs = request.get_json()
        width = grid_specs["width"]
        height = grid_specs["height"]
        current_app.config["GRID"] = Grid(width, height)
        return get_simulation_state()

    @grid_ns.doc('current_state')
    @grid_ns.marshal_with(simulation_state)
    def get(self):
        """ Get the grid's current state """
        if current_app.config["GRID"] is None:
            abort(422, "You must create a simulation space first!")
        return get_simulation_state()
