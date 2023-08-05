from pywizard.worker import worker
from jinja2 import Environment as JinjaEnv


def test_get_template_engine():
    with worker.session():
        isinstance(worker.env.get_template_engine(), JinjaEnv)