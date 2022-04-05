from flask import Flask
from .apis.blueprints import blueprint

app = Flask(__name__)

app.register_blueprint(blueprint, url_prefix='/')
app.config['GRID'] = None
app.config['DINOS'] = {}
app.config['ROBOTS'] = {}

if __name__ == '__main__':  # pragma: no cover
    app.run(debug=True)
