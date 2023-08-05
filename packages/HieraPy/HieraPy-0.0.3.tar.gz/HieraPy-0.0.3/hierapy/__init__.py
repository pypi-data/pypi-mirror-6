import yaml

class HieraPy(object):

    def __init__(self, config_file, folder, lazy_load = True):
        self.__folder = folder
        self.__config_file = config_file
        self.__loaded = False
        self.__config = dict()
        if not lazy_load:
            self.__load_config()

    def get(self, key, default=False):
        '''
        Return value for key in the config dictionary or default if none
        found.
        '''
        if not self.__loaded:
            self.__load_config()

        conf = self.__config
        for part in key.split("/"):
            if conf and part in conf:
                conf = conf[part]
            else:
                conf = None
        if conf is None:
            return default
        else:
            return conf

    def __load_config(self):
        '''
        Read all configuration files into memory
        '''
        base_config = self.__load(self.__config_file)
        for file_name in reversed(base_config[':hierarchy']):
            self.__merge_config(file_name, self.__folder)
        self.__loaded = True

    def __load(self, file_name):
        '''
        Load and parse a given YAML file.
        '''
        with open(file_name, "r") as fp:
            return yaml.load(fp)

    def __merge_config(self, file_name, folder):
        '''
        Loads file_name and merges it into current configuration dictionary.
        '''
        config = self.__load('%s/%s.yaml' % (folder, file_name))
        self.__config = self.__merged(self.__config, config)

    def __merged(self, *args):
        '''
        Merge recursively two dictionaries.
        '''
        out = dict()
        def merge_dict(a, b):
            out = a.copy()
            for k, v in b.items():
                if k in out:
                    if isinstance(v, dict):
                        out[k] = merge_dict(out[k], v)
                    else:
                        out[k] = v
                else:
                    out[k] = v
            return out
        for conf in args:
            out = merge_dict(out, conf)
        return out
