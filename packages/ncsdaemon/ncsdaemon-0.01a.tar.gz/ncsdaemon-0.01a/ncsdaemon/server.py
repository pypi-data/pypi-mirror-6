""" Runs the Flask server for the REST interface """

from flask import Flask, request
from flask.ext.restful import Api
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import json

from ncsdaemon.resources import ReportResource
from ncsdaemon.users import UserManager
from ncsdaemon.util import SchemaLoader
from ncsdaemon.util import ServerUtils
from ncsdaemon.simhelper import SimHelper

API_PREFIX = '/ncs/api'

def register_resources(api):
    api.add_resource(ReportResource)

def register_routes(app):
    """ Registers routes for the Flask application """

    @app.before_request
    def before_request():
        """ This runs before each request, currently ensures a key is in
        the header for all requests aside from the login request """
        user_manager = UserManager()
        token = None
        # If the requested URL doesn't match any routes
        if request.url_rule == None:
            message = ServerUtils.json_message("Invalid request path")
            return ServerUtils.json_and_status(message, 404)
        # If they're trying to login, send them through
        if request.path == API_PREFIX + '/login':
            return
        # Try to get the auth token from the header
        try:
            token = request.headers['token']
        # Return an error if they didn't provide an auth token
        except KeyError:
            if request.path != API_PREFIX + '/login':
                message = ServerUtils.json_message("Authentication Required")
                return ServerUtils.json_and_status(message, 401)
        # check that the token is valid
        try:
            user = user_manager.get_user_from_token(token)
            # add the user to the request object
            request.user = user
        # if the token is not valid return a 401
        except KeyError:
            message = ServerUtils.json_message("Invalid auth token")
            return ServerUtils.json_and_status(message, 401)

    @app.route(API_PREFIX + '/login', methods=['POST'])
    def handle_login_request():
        """ Handles requests for auth tokens """
        schema_loader = SchemaLoader()
        user_manager = UserManager()
        js = {}
        # Ensure the request is valid json
        try:
            js = json.loads(request.get_data())
        except ValueError:
            message = "Invalid request, the request should be a json object"
            json_message = ServerUtils.json_message(message)
            return ServerUtils.json_and_status(json_message, 400)
        # see if the schema works
        try:
            validate(js, schema_loader.get_schema('login_post'))
        # if it doesn't pass validation, return a bad request error
        except ValidationError:
            message = "Improper json format"
            json_message = ServerUtils.json_message(message)
            return ServerUtils.json_and_status(json_message, 400)
        # check user credentials
        is_valid = user_manager.verify_user(js['username'], js['password'])
        # if the credentials are valid, send the token
        if is_valid:
            token = user_manager.get_user_token(js['username'])
            return ServerUtils.json_and_status({ "token": token }, 200)
        # otherwise send a 'Not Authorized'
        else:
            message = "Invalid login credentials"
            json_message = ServerUtils.json_message(message)
            return ServerUtils.json_and_status(json_message, 401)

    @app.route(API_PREFIX + '/sim', methods=['GET', 'POST', 'DELETE'])
    def handle_simulation():
        """ Method to deal with running/querying/stopping a simulation """
        return ''
        sim = SimHelper()
        status = sim.get_status()
        # if requesting info about the simulator
        if request.method == 'GET':
            return ServerUtils.json_and_status(status, 200)
        # if they're trying to run the simulator
        if request.method == 'POST':
            # if theres already a sim running
            if status['status'] == 'running':
                message = "Simulation currently in progress"
                json_message = ServerUtils.json_message(message)
                ServerUtils.json_and_status(json_message, 409)
            # if theres no sim currently running, start one
            if status['status'] == 'idle':
                # get the user from their token
                info = sim.run(request.user.username, None)
                return ServerUtils.json_and_status(info, 200)
        # if they're trying to stop a simulation
        if request.method == 'DELETE':
            # if a sim is running
            if status['status'] == 'running':
                # if the user requesting is the same that ran the sim
                if status['user'] == request.user.username:
                    res = sim.stop()
                    ServerUtils.json_and_status(res, 200)
                # otherwise they are not authorized
                else:
                    message = "You are not authorized to terminate the current simulation"
                    json_message = ServerUtils.json_message(message)
                    return ServerUtils.json_and_status(json_message, 401)
            # if theres no sim running, return a conflict message
            if status['status'] == 'idle':
                message = "No simulation is running"
                json_message = ServerUtils.json_message(message)
                return ServerUtils.json_and_status(json_message, 409)

    @app.route(API_PREFIX + '/sim/<simid>', methods=['GET', 'POST', 'DELETE'])
    def handle_prior_simulation():
        return ''

class Server(object):
    """ Rest server class """

    def run(self, host, port):
        """ Runs the REST server """
        self.app.run(host, port)

    def __init__(self):
        # Create new application
        self.app = Flask(__name__)
        # Debugging is okay for now
        self.app.debug = True
        # Create the REST API
        self.api = Api(self.app)
        # Register application resources
        register_resources(self.api)
        # Register application routes
        register_routes(self.app)
