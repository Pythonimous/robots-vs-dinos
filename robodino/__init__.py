from flask import Flask
from .apis import api

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/')
app.config['GRID'] = None
app.config['DINOSAURS'] = {}
app.config['ROBOTS'] = {}

if __name__ == '__main__':
    app.run(debug=True)
