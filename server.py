#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You can start this by executing it in python:
# python server.py
#
# remember to:
#     pip install flask

import flask
from flask import Flask, request, redirect, url_for, send_from_directory
import json
app = Flask(__name__)
app.debug = True

# An example world
# {
#    'a':{'x':1, 'y':2},
#    'b':{'x':2, 'y':3}
# }


class World:
    def __init__(self):
        self.clear()

    def update(self, entity, key, value):
        entry = self.space.get(entity, dict())
        entry[key] = value
        self.space[entity] = entry

    def set(self, entity, data):
        self.space[entity] = data

    def clear(self):
        self.space = dict()

    def get(self, entity):
        return self.space.get(entity, dict())

    def world(self):
        return self.space

# you can test your webservice from the commandline
# curl -v -H "Content-Type: application/json" -X PUT http://127.0.0.1:5000/entity/X -d '{"x":1,"y":1}'


myWorld = World()

# I give this to you, this is how you get the raw body/data portion of a post
# in n flask this should come with flask but whatever, it's not my project.


def generate_OK_json_response(data):
    response = app.response_class(
                response=json.dumps(data),
                status=200,
                mimetype='application/json')
    return response


def flask_post_json():
    '''Ah the joys of frameworks! They do so much work for you
       that they get in the way of sane operation!'''
    if (request.json is not None):
        return request.json
    elif (request.data is not None and request.data.decode("utf8") != u''):
        return json.loads(request.data.decode("utf8"))
    else:
        return json.loads(request.form.keys()[0])


@app.route("/")
def hello():
    # need to change this up
    '''Return something coherent here. Or redirect to /static/index.html'''
    return redirect("/static/index.html")

@app.route('/static/<path:path>')
def send_path(path):
    return send_from_directory('static', path)

@app.route("/entity/<entity>", methods=['POST', 'PUT'])
def update(entity):
    '''update the entities via this interface'''
    data = flask_post_json()
    for key in data:
        myWorld.update(entity, key, data[key])
    return generate_OK_json_response(data)


@app.route("/world", methods=['POST', 'GET'])
def world():
    '''you should probably return the world here'''
    old_world = flask_post_json()
    curr_world = myWorld.world()
    if not old_world:
        updates = curr_world
    else:
        updates = {k:v for k,v in curr_world.items() if k not in old_world or v != old_world[k]}
    return generate_OK_json_response(updates)


@app.route("/entity/<entity>")
def get_entity(entity):
    '''GET version of the entity interface.
    Return a representation of the entity'''
    data = myWorld.get(entity)
    return generate_OK_json_response(data)


@app.route("/clear", methods=['POST', 'GET'])
def clear():
    '''Clear the world out!'''
    data = dict()
    myWorld.clear()
    return generate_OK_json_response(data)


if __name__ == "__main__":
    app.run()
