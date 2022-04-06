from flask_restx import Api

from flask import Blueprint

from .grid_ns import grid_ns
from .robot_ns import robot_ns
from .dino_ns import dino_ns

blueprint = Blueprint('SimulationBlueprint', __name__)
api = Api(blueprint, title='Robots vs Dinos', description='Robots vs Dinos Endpoints')

api.add_namespace(grid_ns, path='/grid')
api.add_namespace(robot_ns, path='/robots')
api.add_namespace(dino_ns, path='/dinos')
