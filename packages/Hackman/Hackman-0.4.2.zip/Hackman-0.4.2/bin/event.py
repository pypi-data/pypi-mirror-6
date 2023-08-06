class Event(dict):

    def __init__(self, data_event):
        for key, data in data_event.items():
            if isinstance(data, dict):
                self.__dict__[key] = Event(data)
            else:
                self.__dict__[key] = data

    def __getattr__(self, name):
        if name in self.iterkeys():
            return self[name]
        raise AttributeError('%s has no property named %s.' % (self.__class__.__name__, name))

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.__dict__.__repr__())