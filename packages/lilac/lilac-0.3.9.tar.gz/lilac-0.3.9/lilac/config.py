# coding=utf8

"""Configuration manager, config is in toml"""

from . import charset
from .exceptions import ConfigSyntaxError

import toml
from os.path import join
from os.path import exists


class Config(object):
    """Configuration manager"""

    filename = "config.toml"
    filepath = join(".", filename)
    # default configuration
    default = {
        'root_path': '',
        'blog': {
            'name': 'Sunshine Every Day',
            'description': 'Never give up',
            'url': 'http://your-site.com',
            'theme': 'less'
        },
        'author': {
            'name': 'hit9',
            'email': 'nz2324@126.com'
        },
        'disqus': {
            'shortname': ''  # empty to disable comment ability
        }
    }

    def read(self):
        """Read and parse config, return a dict"""

        if not exists(self.filepath):
            # if not exists, touch one
            open(self.filepath, "a").close()

        content = open(self.filepath).read().decode(charset)
        try:
            config = toml.loads(content)
        except toml.TomlSyntaxError:
            raise ConfigSyntaxError

        return config

config = Config()  # build a config instance
