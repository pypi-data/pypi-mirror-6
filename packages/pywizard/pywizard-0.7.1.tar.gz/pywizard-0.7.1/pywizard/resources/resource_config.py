from logging import debug

from iniparse import ConfigParser
import yaml

from pywizard.core.env import worker
from pywizard.events import event
from pywizard.resources.python import PythonResource


def ini_file(
        filename,
        config,
        strict_sections=False,
        on_apply=None
):

    def _apply():
        debug('Write ini settings to %s' % filename)
        debug(config)

        cfg = ConfigParser()
        cfg.read(filename)
        for section, values in config.items():
            if not cfg.has_section(section):
                if strict_sections:
                    raise Exception('No section %s in ini file %s' % (section, filename))
                else:
                    cfg.add_section(section)

            for key, val in values.items():
                cfg.set(section, key, val)

        with open(filename, 'w') as configfile:
            cfg.write(configfile)

        event(on_apply)

    worker.register_resource(
        PythonResource(
            _apply,
            description='Ini file'
        )
    )


def yaml_file(
        filename,
        config
):

    def dict_sum(d1, d2):
        if d1 is None:
            return d2
        if d2 is None:
            return d1
        if isinstance(d1, list) and isinstance(d2, list):
            return list(set(d1 + d2))
        try:
            return d1 + d2
        except TypeError:
            # assume d1 and d2 are dictionaries
            keys = set(d1.keys()) | set(d2.keys())
            return dict((key, dict_sum(d1.get(key), d2.get(key))) for key in keys)

    def _apply():
        debug('Write yaml settings to %s' % filename)
        debug(config)

        cfg = yaml.load(file(filename, 'r'))    # 'document.yaml' contains a single YAML document.
        cfg = dict_sum(cfg, config)
        with open(filename, 'w') as configfile:
            yaml.dump(cfg, configfile)

    worker.register_resource(
        PythonResource(
            _apply,
            description='Ini file'
        )
    )