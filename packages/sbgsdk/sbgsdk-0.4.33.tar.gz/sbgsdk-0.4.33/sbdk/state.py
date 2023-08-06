from os.path import join, exists
import json


class State(dict):
    """ Utility class to handle sbdk state file. NOT THREAD SAFE """

    FILENAME = 'state.json'

    def __init__(self, path):
        self.state_file = join(path, State.FILENAME)
        d = {}
        if exists(self.state_file):
            with open(self.state_file) as f:
                d = json.load(f)
        dict.__init__(self, d)

    def save(self):
        with open(self.state_file, 'w') as f:
            json.dump(self, f)

    def __enter__(self):
        return self

    def __exit__(self):
        self.save()
