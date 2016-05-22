import base64
import hashlib
import hmac
from functools import wraps

from flask import request
from flask import jsonify
from datetime import datetime
import time


class Hmac(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_self(app)


    def init_self(self, app):
        self.hmac_key = app.config['HMAC_KEY']
        self.hmac_disarm = app.config.get('HMAC_DISARM', False)


    def check_hmac(self, route_view_function):
        @wraps(route_view_function)
        def decorated_view_function(*args, **kwargs):
            if self.hmac_disarm == True:
                return route_view_function(*args, **kwargs)
            else:
                try:
                    hmac_token = request.headers['HMAC']
                    expiration = request.headers['expiration']
                    hidden_index = int(expiration[7]) + 8
                    new_expiration = expiration[:hidden_index] + expiration[hidden_index+1:]
                    new_expiration = new_expiration[:7] + new_expiration[8:]
                    data = base64.b64decode(new_expiration)
                    a = data
                    d = datetime.strptime(a, "%m/%d/%Y %H:%M:%S")
                    converted_time = time.mktime(d.timetuple())
                    if time.time() - converted_time > 20000:
                        '''
                        We check the expiration date in every request in order to recognize
                        whether the request is created recently regardless the including data.
                        '''
                        message = {'status': '403', 'message': 'not authorized'}
                        response = jsonify(message)
                        response.status_code = 403
                        return response
                except:
                    message = {'status': '403', 'message': 'not authorized'}
                    response = jsonify(message)
                    response.status_code = 403
                    return response


                if self.compare_hmacs(self.hmac_key, request.data, hmac_token) == True:
                    return route_view_function(*args, **kwargs)
                else:
                    message = {'status': '403', 'message':'not authorized'}
                    response = jsonify(message)
                    response.status_code = 403
                    return response
        return decorated_view_function


    def make_hmac(self, secret, data, digestmod=None):
        if digestmod == None:
            digestmod = hashlib.sha256
        try:
            hmac_token = hmac.new(secret, data, digestmod=digestmod)
            return hmac_token
        except TypeError as err:
            raise err


    def render_hmac(self, secret, data):
        hmac_token_server = self.make_hmac(secret, data).hexdigest()
        return hmac_token_server


    def compare_hmacs(self, secret, data, hmac_token_client):
        hmac_token_server = self.render_hmac(secret, data)
        if hmac_token_client == hmac_token_server.upper():
            return True
        else:
            return False
