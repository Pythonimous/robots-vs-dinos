from flask_restx import Resource, abort, Namespace, fields
from flask import request, current_app

from .grid_ns import simulation_state, get_simulation_state

from robodino.core.characters import Dino


dino_ns = Namespace('Dino', description='Dino related endpoints')

dino_in = dino_ns.model('BuildDino', {
    'coordinates': fields.List(fields.Integer, required=True,
                               min_items=2, max_items=2,
                               description='X, Y coordinates'),
    'health': fields.Integer(required=True, min=1, default=2,
                             description="Dino's health")
})

dino_out = dino_ns.inherit('GetDino', dino_in, {
    'id': fields.String(required=True, description='Unique dino id')
})

dino_healthbar = dino_ns.model("Healthbar", {
    'id': fields.String(required=True, description='Unique dino id'),
    'healthbar': fields.String(description="Dino healthbar")
})


@dino_ns.route('/')
class Dinos(Resource):
    @dino_ns.doc('list_dinos')
    @dino_ns.marshal_list_with(dino_out)
    def get(self):
        """ Get a list of currently existing dinos """
        dinos_info = [dino.info()
                      for dino in current_app.config["DINOS"].values()]
        return dinos_info

    @dino_ns.doc('create_dino')
    @dino_ns.expect(dino_in, code=201)
    @dino_ns.marshal_with(simulation_state)
    def post(self):
        """ Create a dino given its coordinates and health """
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
                       f"X should be in [0; {width-1}]. "
                       f"Y should be in [0; {height-1}].")
        if grid.tile(x, y).has():
            abort(409, 'Tile not empty.')

        health = dino_specs['health']
        dino = Dino(dino_id, x, y, current_app.config['GRID'], health=health)
        current_app.config['DINOS'][dino_id] = dino

        return get_simulation_state()


@dino_ns.route('/<dino_id>')
@dino_ns.param('dino_id', 'The dino identifier')
@dino_ns.response(404, 'Dino not found')
class GetDino(Resource):
    @dino_ns.doc('get_dino')
    @dino_ns.marshal_with(dino_out)
    def get(self, dino_id):
        """ Get the <id> dino info """
        if dino_id in current_app.config["DINOS"]:
            return current_app.config["DINOS"][dino_id].info()
        else:
            abort(404, message='Dino not found.')


@dino_ns.route('/health')
class DinosHealth(Resource):
    @dino_ns.doc('dinos_health')
    @dino_ns.marshal_list_with(dino_healthbar)
    def get(self):
        """ Get healthbars for all dinos """
        healthbars = [{"id": dino_id, "healthbar": dino.healthbar()}
                      for dino_id, dino in current_app.config["DINOS"].items()]
        return healthbars


@dino_ns.route('/<dino_id>/health')
@dino_ns.param('dino_id', 'The dino identifier')
@dino_ns.response(404, 'Dino not found')
class DinoHealth(Resource):
    @dino_ns.doc('dino_health')
    @dino_ns.marshal_with(dino_healthbar)
    def get(self, dino_id):
        """ Get a healthbar for the <id> dino """
        if dino_id in current_app.config["DINOS"]:
            dino = current_app.config["DINOS"][dino_id]
            return {"id": dino_id,
                    "healthbar": dino.healthbar()}
        else:
            abort(404, message='Dino not found.')
