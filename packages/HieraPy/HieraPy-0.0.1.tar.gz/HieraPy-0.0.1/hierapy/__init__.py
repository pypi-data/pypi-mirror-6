import yaml

class HieraConfig(object):
    def __init__(self, config_file, folder):
        self.__config = dict()
        base_config = self.__load(config_file)
        for file_name in reversed(base_config[':hierarchy']):
            self.__merge_config(file_name, folder)

    def get(self, key, default=False):
        '''
        Return value for key in the config dictionary or default if none
        found
        '''
        if self.__config and key in self.__config:
            return self.__config[key]
        else:
            return default

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
        Merge recursively two dictionaries and return the result.
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
