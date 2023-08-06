import json
import logging

import mosaik_api
import networkx as nx

from mosaik_web import server


logger = logging.getLogger('mosaik_web.mosaik')

meta = {
    'models': {
        'Topology': {
            'public': True,
            'params': ['gridfile'],
            'attrs': [],
        }
    },
}

# TODO: Document config file format
default_config = {
    'ignore_types': ['Topology'],
    'merge_types': ['Branch', 'Transformer'],
    'etypes': {},
}


class MosaikWeb(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(meta)
        self.step_size = None
        self.server = None
        self.eid = None
        self.ignore_types = default_config['ignore_types']
        self.merge_types = default_config['merge_types']
        self.etype_conf = default_config['etypes']

    def configure(self, args, backend, env):
        """Start a wevserver for the visualization."""
        server_addr = mosaik_api._parse_addr(args['--serve'])
        server_sock = backend.TCPSocket.server(env, server_addr)
        self.server = server.Server(env, server_sock)

    def init(self, step_size, config_file):
        self.step_size = step_size

        config = json.load(open(config_file))
        if 'ignore_types' in config:
            self.ignore_types = config['ignore_types']
        if 'merge_types' in config:
            self.merge_types = config['merge_types']
        if 'etypes' in config:
            self.etype_conf.update(config['etypes'])

        return self.meta

    def create(self, num, model):
        if num != 1 or self.eid is not None:
            raise ValueError('Can only one grid instance.')
        if model != 'Topology':
            raise ValueError('Unknown model: "%s"' % model)

        self.eid = 'topo'

        return [{'eid': self.eid, 'type': model, 'rel': []}]

    def step(self, time, inputs):
        if not self.server.topology:
            logger.info('Creating topology ...')
            entities = yield self.mosaik.get_related_entities(self.eid)
            entities = entities[self.eid]
            self.related_entities = entities

            rel_eids = [eid for eid, _ in entities]
            relations = yield self.mosaik.get_related_entities(*rel_eids)

            self._build_topology(entities, relations)
            logger.info('Topology created')

        progress = yield self.mosaik.get_progress()

        req_attrs = {}
        for eid, etype in self.related_entities:
            if etype not in self.etype_conf:
                continue
            req_attrs[eid] = [self.etype_conf[etype]['attr']]
        data = yield self.mosaik.get_data(req_attrs)

        node_data = {}
        for node in self.server.topology['nodes']:
            node_id = node['name']
            try:
                attr = self.etype_conf[node['type']]['attr']
            except KeyError:
                val = 0
            else:
                val = data[node_id][attr]
            node_data[node_id] = {
                'value': val,
            }
        self.server.set_new_data({
            'progress': progress,
            'nodes': node_data,
        })

        return time + self.step_size

    def get_data(self, outputs):
        return {}

    def _build_topology(self, entities, relations):
        # First, we create a directed graph to merge all edge pairs
        # [(x, y), (y, x)] to (x, y):
        nxg = nx.DiGraph()
        for eid, etype in entities:
            if etype in self.ignore_types or etype in self.merge_types:
                continue
            nxg.add_node(eid, type=etype)

            for rel_eid, rel_etype in relations[eid]:
                if rel_etype in self.ignore_types:
                    continue

                if rel_etype in self.merge_types:
                    # Remove branches/transformers, but relate their adjacent
                    # nodes/buses:
                    rels = [r[0] for r in relations[rel_eid]]
                    rels.remove(eid)
                    rel_eid = rels[0]

                edge = list(sorted([eid, rel_eid]))
                # TODO: Get edge length for Branch type
                nxg.add_edge(edge[0], edge[1], length=0)

        # Now we can build the topology for D3JS
        # We have to use two loops to make sure "node_idx" is filled for the
        # second one.
        self.server.topology = {
            'etypes': self.etype_conf,
            'nodes': [],
            'links': [],
        }
        topology = self.server.topology
        node_idx = {}

        for node, attrs in nxg.node.items():
            node_idx[node] = len(topology['nodes'])
            type = attrs['type']
            topology['nodes'].append({
                'name': node,
                'type': type,
                'value': 0,
            })

        for source, targets in nxg.adj.items():
            for target, attrs in targets.items():
                topology['links'].append({
                    'source': node_idx[source],
                    'target': node_idx[target],
                    'length': attrs['length'],
                })

        self.server.topology_ready.succeed()


def main():
    desc = 'Simple visualization for mosaik simulations'
    extra_opts = [
        '-s HOST:PORT, --serve=HOST:PORT    ',
        ('            Host and port for the webserver '
         '[default: 127.0.0.1:8000]'),
    ]
    mosaik_api.start_simulation(MosaikWeb(), desc, extra_opts)
