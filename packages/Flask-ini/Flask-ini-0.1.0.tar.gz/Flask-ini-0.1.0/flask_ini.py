import ConfigParser
import warnings
import datetime

from flask import current_app

class FlaskIni(ConfigParser.SafeConfigParser):
    '''Subclass of ConfigParser.SafeConfigParser that must be run inside a
    flask app context. It looks for a special [flask] section of the config
    file and uses that to configure flask's own built-in variables.'''

    def read(self, *args, **kwargs):
        '''Overridden read() method to call parse_flask_section() at the end'''
        ret = ConfigParser.SafeConfigParser.read(self, *args, **kwargs)
        self.parse_flask_section()
        return ret

    def readfp(self, *args, **kwargs):
        '''Overridden readfp() method to call parse_flask_section() at the
        end'''
        ret = ConfigParser.SafeConfigParser.readfp(self, *args, **kwargs)
        self.parse_flask_section()
        return ret

    def parse_flask_section(self):
        '''Parse the [flask] section of your config and hand off the config
        to the app in context.

        Config vars should have the same name as their flask equivalent except
        in all lower-case.'''
        if self.has_section('flask'):
            for item in self.items('flask'):
                self._load_item(item[0])
        else:
            warnings.warn("No [flask] section found in config")


    def _load_item(self, key):
        '''Load the specified item from the [flask] section. Type is
        determined by the type of the equivalent value in app.default_config
        or string if unknown.'''
        key_u   = key.upper()
        default = current_app.default_config.get(key_u)

        # One of the default config vars is a timedelta - interpret it
        # as an int and construct using it
        if type(default) is datetime.timedelta:
            current_app.config[key_u] = datetime.timedelta(self.getint('flask', key))
        elif type(default) is bool:
            current_app.config[key_u] = self.getboolean('flask', key)
        elif type(default) is float:
            current_app.config[key_u] = self.getfloat('flask', key)
        elif type(default) is int:
            current_app.config[key_u] = self.getint('flask', key)
        else:
            current_app.config[key_u] = self.get('flask', key)
