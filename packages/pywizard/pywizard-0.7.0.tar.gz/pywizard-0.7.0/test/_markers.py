
import os
import pytest


def __is_container():
    return 'container' in os.environ and os.environ['container'] == 'lxc'

in_docker = pytest.mark.skipif(not __is_container(), reason="Run only inside docker container")