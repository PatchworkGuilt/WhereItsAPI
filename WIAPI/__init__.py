import os
from flask import Flask
from flask.ext import restful
from flask.ext.sqlalchemy import SQLAlchemy
from flask import make_response
from bson.json_util import dumps

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)
db.create_all()

app.debug = True

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Origin, X-Requested-With,Content-Type, Accept,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response

def output_json(obj, code, headers=None):
    resp = make_response(dumps(obj), code)
    resp.headers.extend(headers or {})
    return resp

DEFAULT_REPRESENTATIONS = {'application/json': output_json}
api = restful.Api(app)
api.representations = DEFAULT_REPRESENTATIONS

import WIAPI.resources
