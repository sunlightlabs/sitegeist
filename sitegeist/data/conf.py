import ConfigParser

settings = {}


def load_config(path):

    config = ConfigParser.RawConfigParser()
    config.read(path)

    for key, val in config.items('core'):
        settings[key] = val
