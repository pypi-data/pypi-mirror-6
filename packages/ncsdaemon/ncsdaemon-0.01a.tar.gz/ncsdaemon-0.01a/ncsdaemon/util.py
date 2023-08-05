""" Loads JSON schema objects for validation """
import os
import sys
from contextlib import contextmanager
import json
from flask import jsonify

class ServerUtils(object):
    """ Miscellaneous server utilities """

    @classmethod
    def json_and_status(cls, json, status):
        res = jsonify(json)
        res.status_code = status
        return res

    @classmethod
    def json_message(cls, message):
        return {"message": message}

class SchemaLoader(object):
    """ Schema Loader Singleton """
    _instance = None

    DIRECTORY = 'json_schemas/'

    SCHEMAS = {
        "login_post": DIRECTORY + 'login_post.json'
    }

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SchemaLoader, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.schema_dicts = {}
        for schema_name in self.SCHEMAS:
            schema_file = self.SCHEMAS[schema_name]
            with open(schema_file) as f:
                self.schema_dicts[schema_name] = json.loads(f.read())

    def get_schema(self, name):
        return self.schema_dicts[name]

class WriteRedirect(object):

    @classmethod
    @contextmanager
    def stdout_redirected(cls, to=os.devnull):
        '''
        import os

        with stdout_redirected(to=filename):
            print("from Python")
            os.system("echo non-Python applications are also supported")
        '''
        fd = sys.stdout.fileno()

        ##### assert that Python and C stdio write using the same file descriptor
        ####assert libc.fileno(ctypes.c_void_p.in_dll(libc, "stdout")) == fd == 1

        def _redirect_stdout(to):
            sys.stdout.close() # + implicit flush()
            os.dup2(to.fileno(), fd) # fd writes to 'to' file
            sys.stdout = os.fdopen(fd, 'w') # Python writes to fd

        with os.fdopen(os.dup(fd), 'w') as old_stdout:
            with open(to, 'w') as file:
                _redirect_stdout(to=file)
            try:
                yield # allow code to be run with the redirected stdout
            finally:
                _redirect_stdout(to=old_stdout) # restore stdout.
                                                # buffering and flags such as
                                                # CLOEXEC may be different


