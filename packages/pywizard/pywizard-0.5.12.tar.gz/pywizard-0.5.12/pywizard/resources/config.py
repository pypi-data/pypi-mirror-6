from logging import debug
import os
import subprocess
from tempfile import NamedTemporaryFile
from iniparse import ConfigParser
from pywizard.utils.events import event
import yaml
from pywizard.utils.process import run
from pywizard.resources.python import PythonResource
from pywizard.templating import compile_content
from pywizard.worker import worker


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
        for section, values in config.iteritems():
            if not cfg.has_section(section):
                if strict_sections:
                    raise Exception('No section %s in ini file %s' % (section, filename))
                else:
                    cfg.add_section(section)

            for key, val in values.iteritems():
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
            keys = set(d1.iterkeys()) | set(d2.iterkeys())
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
