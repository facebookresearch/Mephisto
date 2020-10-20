import os
import json
import random


class SquadQADataLoader():

    def __init__(self, opt, shared=None):
        if opt['datatype'].startswith('train'):
            suffix = 'train'
        elif opt['datatype'].startswith('dev'):
            suffix = 'dev'
        else:
            suffix = 'custom'
        opt['datafile'] = os.path.join(
            opt['datapath'], 'SQuAD', suffix + '-v1.1.json')
        self.data = []
        for item in self.setup_data(opt['datafile']):
            self.data.append(item)

    def setup_data(self, path):
        print('loading: ' + path)
        with open(path) as data_file:
            self.squad = json.load(data_file)['data']
        for paragraph in self.squad:
            yield paragraph

    def act(self):
        idx = random.randrange(len(self.data))
        return self.data[idx]

    def get(self, id):
        for item in self.data:
            if item["id"] == id:
                return item
