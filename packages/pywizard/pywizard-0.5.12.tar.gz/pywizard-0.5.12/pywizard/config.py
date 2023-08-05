"""

"""
import argparse
import json
import logging
import sys
import yaml


def pywizard_cfg_cmd():

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str)
    parser.add_argument('--node-name', type=str)
    parser.add_argument('--log-level', type=str, nargs='?')
    parser.set_defaults(log_level='INFO')

    args = parser.parse_args()

    logging.basicConfig(level=logging.getLevelName(args.log_level))

    data = yaml.load(open(args.config))

    def node_context(name, config):
        node_context = config['provision']['info']
        node_context['ip'] = config['ip']
        node_context['name'] = name
        node_context['roles'] = config['provision']['roles']
        return node_context

    sys.stdout.write(json.dumps({
        'me': node_context(args.node_name, data['nodes'][args.node_name]),
        'all': [node_context(name, config) for name, config in data['nodes'].iteritems()]
    }))