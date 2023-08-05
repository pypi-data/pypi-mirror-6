"""
Module provides integration with template engines.
"""
from logging import debug
from jinja2.loaders import FileSystemLoader

from pywizard.worker import worker


def jinja2_templates(template_directory=None):
    if template_directory:
        debug('New template path: %s' % template_directory)
        worker.env.template_loaders.insert(0, FileSystemLoader(template_directory))


def compile_content(content):
    """
    Check if content is callable and calls it to generate content.
    If not just cast to string.

    @param content:
    @return:
    """
    if callable(content):
        content_compiled = content()
    else:
        content_compiled = content

    if isinstance(content_compiled, unicode):
        content_compiled = content_compiled.encode("utf-8")

    return content_compiled


def tpl(name, context=None):
    """
    Generates function that will be called during resource apply process.
    Usually used in resources thar require some big text-like values. Like this:
    file('foo.conf', content=from_template('foo.conf.tpl'))

    Currently there is no direct relation with Jinja2 for templates, so any template engine
    may be used. The only thing to do is to implement simple class that has get_template(name)
    method.
    With Jinja2, however, you can directly use it's template engine.

    @param name: string name of temp[late, exact value depends on template engine configuration
    @param context: dict with variables, context for template rendering
    @return: callable function that will be used for template render
    """

    if context is None:
        context = {}

    def render_template():
        """
        Lookups template, and render it
        @return: string
        """
        tpl = worker.env.get_template_engine().get_template(name)
        return tpl.render(context)

    return render_template