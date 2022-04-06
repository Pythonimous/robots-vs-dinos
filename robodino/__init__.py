from flask import Flask

from .apis import blueprint


def create_app(name=None):
    app = Flask(name or __name__)
    app.register_blueprint(blueprint)
    app.config['GRID'] = None
    app.config['DINOS'] = {}
    app.config['ROBOTS'] = {}
    return app


if __name__ == '__main__':  # pragma: no cover
    app = create_app()
    app.run(debug=True)
