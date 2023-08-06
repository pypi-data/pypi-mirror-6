# coding=utf-8
from jinja2 import Environment, DictLoader
from jinja2.exceptions import UndefinedError
import pytest
from pywizard.context import Context
from pywizard.templating import jinja, compile_content


def test_template_render():

    with jinja(loader=DictLoader({'index.html': '--{{ foo }}--'})) as tpl:

        callback = tpl('index.html', {'foo': 123})
        assert callback() == '--123--'

        callback = tpl('index.html', {'foo': 321})
        assert callback() == '--321--'

        with pytest.raises(UndefinedError):
            callback = tpl('index.html')
            callback()


def test_compile_content():

    def boo():
        return 'foo'

    # callable. will extract result
    assert compile_content(boo) == 'foo'

    # string, just return
    assert compile_content('boo') == 'boo'