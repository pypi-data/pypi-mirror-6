# coding=utf-8
from jinja2 import Environment, DictLoader
from pywizard.worker import worker
from pywizard.templating import tpl, jinja2_templates, compile_content


def test_template_render():

    with worker.session():

        worker.env.template_engine = Environment(loader=DictLoader({'index.html': '--{{ foo }}--'}))

        callback = tpl('index.html', {'foo': 123})
        assert callback() == '--123--'

        callback = tpl('index.html')
        assert callback() == '----'


def test_jinja2_templates():
    with worker.session():
        assert len(worker.env.template_loaders) == 0
        jinja2_templates(template_directory='foo/bar/baz')

        assert len(worker.env.template_loaders) == 1
        assert worker.env.template_loaders[0].searchpath == ['foo/bar/baz']

def test_compile_content():
    """


    @return:
    """

    def boo():
        return 'foo'

    # callable. will extract result
    assert compile_content(boo) == 'foo'

    # string, just return
    assert compile_content('boo') == 'boo'

    assert compile_content(u'бебе') == u'бебе'.encode("utf-8")