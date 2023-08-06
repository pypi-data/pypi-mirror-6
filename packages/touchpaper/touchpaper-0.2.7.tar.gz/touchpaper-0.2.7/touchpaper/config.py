import json

from os import getcwd
from os.path import exists, expanduser, join


'''
The global config object
'''
class Config():
    RC_FILE_NAME = '.touchpaperrc'

    AWS_KEY_ENV_VAR = 'AWS_ACCESS_KEY_ID'
    AWS_SECRET_ENV_VAR = 'AWS_SECRET_ACCESS_KEY'

    RUNNING_STATE = 'running'

    data = False
    path = False

    def find(self, **kwargs):
        '''
        Search the current user's home directory, or the current directory, for
        our rc file.
        '''
        local_config_path = join(getcwd(), self.RC_FILE_NAME)
        home_config_path = join(expanduser('~'), self.RC_FILE_NAME)
        config_path = False
        config = False

        if 'location_override' in kwargs:
            if exists(kwargs['location_override']):
                config_path = kwargs['location_override']
        else:
            if exists(local_config_path):
                config_path = local_config_path
            elif exists(home_config_path):
                config_path = home_config_path
        return config_path

    def get_default(self, name):
        '''
        Return a default value for a given prompt from config data
        '''
        if self.data and 'defaults' in self.data and name in self.data['defaults']:
            return self.data['defaults'][name]
        return None

    def load(self, **kwargs):
        '''
        Parse the config file
        '''
        self.path = self.find()
        if self.path:
            with open(self.path) as f:
                data = json.load(f)
                self.data = data
        return self

    def set_default(self, name, value):
        '''
        Update the stored default value for a given prompt
        '''
        if self.data:
            if 'defaults' not in self.data:
                self.data['defaults'] = {}
            self.data['defaults'][name] = value
            self.save()
        return self

    def save(self):
        '''
        Write the updated config data out to the original config file
        '''
        if self.path:
            with open(self.path, 'w') as f:
                json.dump(self.data, f, sort_keys=True, indent=4)
        return self


config = False


def get_config(**kwargs):
    global config
    if config is False:
        config = Config()
    return config
