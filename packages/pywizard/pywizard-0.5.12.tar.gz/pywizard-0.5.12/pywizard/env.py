"""
Environment is used as central point for configuration
of any kind.
"""
from jinja2.loaders import ChoiceLoader
from jinja2 import Environment as JinjaEnv, StrictUndefined

class Environment(object):
    """
    Provides central place for data exchange
    """

    provision_path = None
    requirements = None
    template_engine = None
    template_loaders = None
    roles = None
    context = None
    interactive = False # True means we can ask user for input

    def __init__(self, template_engine=None):
        self.template_engine = template_engine
        self.requirements = []
        self.template_loaders = []
        self.roles = []

    def get_template_engine(self):
        if not self.template_engine:
            self.template_engine = JinjaEnv(
                loader=ChoiceLoader(self.template_loaders),
                undefined=StrictUndefined
            )
        return self.template_engine

    def context_property(self, property_name, default=None, optional=False):
        if not property_name in self.context['me']:
            if optional:
                return default
            else:
                raise Exception('Can not read property "%s". No value for node "%s" ' % (
                    property_name, self.context['me']['name']
                ))
        else:
            return self.context['me'][property_name]

    def collect_context_property(self, property_name, role=None, allow_empty=False):

        collected = []

        for node in self.context['all']:
            if (not role or role in node['roles']) and property_name in node:
                collected.append(node[property_name])

        if len(collected) < 1 and not allow_empty:
            raise Exception('Can not collect property "%s" no values found across nodes: %s' % (
                property_name, ', '.join([x['name'] for x in self.context['all']])
            ))

        return collected




