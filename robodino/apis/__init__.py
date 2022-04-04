from flask_restx import Api

from .characters import api as char_endpoints

api = Api(
    title='RobotsVsDinos',
    version='1.0',
    description='RESTful API for Grover "Robots vs Dinos" task',
)

api.add_namespace(char_endpoints)

