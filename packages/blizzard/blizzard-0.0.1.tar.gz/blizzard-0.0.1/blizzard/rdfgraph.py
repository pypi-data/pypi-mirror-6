# See https://github.com/RDFLib/rdflib/blob/master/examples/simple_example.py

import rdflib

from rdflib.namespace import Namespace

DATASET = Namespace('http://blizzard.thomaslevine.com/elements/dataset')

class Graph(rdflib.Graph):
    def __init__(self):
        rdflib.Graph.__init__(self)
        # self.bind

    def add_dataset(self, dataset):
        dataset_id = (dataset['catalog'], dataset['datasetid'])
        self.add_node(dataset_id, kind = 'dataset')
        for unique_index in dataset['unique_indices']:
            i = tuple(sorted(unique_index))
            self.add_node(i, kind = 'index')
            self.add_edge(i, dataset_id)
