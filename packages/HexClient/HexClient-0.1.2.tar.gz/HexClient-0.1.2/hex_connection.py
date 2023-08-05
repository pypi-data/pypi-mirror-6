import json
import requests

class HexCommunicationError(Exception):
    pass

class HexConnection(object):
    """Takes care of talking with the hex server."""

    def __init__(self, hex_server='http://hex.local'):
        self.hex_server = hex_server

    def setup(self, password):
        return self.api_request('/api/setup', 'post', data={'password': password})

    def authenticate(self, name, spirit_animal):
        """Checks whether the given name and spirit animal match an account on 
        the hex. If you know your name and spirit animal, there's no need to use
        this method."""
        response = self.api_request("/api/users/authenticate", 'post',
                data={'name': name, 'spirit_animal': spirit_animal})
        return response['result'] == 'OK'

    def get_user(self, name):
        "Gets information about a user by name"
        return self.api_request("/api/users/%s" % name, 'get')

    def get_users(self):
        "Gets a list of all users"
        return self.api_request('/api/users', 'get')

    def create_user(self, name, spirit_animal):
        "Creates a user with the provided name and spirit animal"
        return self.api_request("/api/users", "post", 
                {'name': name, 'spirit_animal': spirit_animal})

    def create_spell(self, user_name, spirit_animal, name, spell):
        """Creates a spell. If there is no spell currently running, the spell 
        will run immediately. Otherwise, the spell will be queued and will run
        when the previous spells have run. You can see the spell queue at 
        http:/hex.local"""
        return self.api_request('/api/spells', 'post',
                {'user_name': user_name, 'spirit_animal': spirit_animal, 'name': name, 
                'setup': spell['setup'], 'loop': spell['loop']})

    jsonHeaders = {
        "Content-Type": 'application/json', 
        'Accept': 'application/json'
    }

    def api_request(self, path, method, data=None):
        methods = {
            'get': requests.get,
            'post': requests.post
        }
        response = methods[method](self.hex_server + path, 
                data=json.dumps(data), headers=self.jsonHeaders)
        if response.status_code != 200:
            raise HexCommunicationError()
        return json.loads(response.content)

if __name__ == '__main__':
    hc = HexConnection()
    hc.get_users()['users']
    hc.get_user('chris')['user']
    assert hc.authenticate('chris', 'eerie bison') == True
