"""
Module provides integration with template engines.
"""
from contextlib import contextmanager

from jinja2 import Environment as JinjaEnv, StrictUndefined, PackageLoader
import collections


def compile_content(content):
    """
    Check if content is callable and calls it to generate content.
    If not, then just cast to string.

    @param content:
    @return:
    """
    if isinstance(content, collections.Callable):
        content_compiled = content()
    else:
        content_compiled = content

    #if isinstance(content_compiled, str):
    #    content_compiled = content_compiled.encode("utf-8")

    return content_compiled


@contextmanager
def jinja(loader, strict=True):
    engine = JinjaEnv(
        loader=loader,
        undefined=StrictUndefined if strict else None
    )

    def tpl(name, context=None):
        """
        Generates function that will be called during resource apply process.
        Usually used in resources thar require some big text-like values. Like this::

            file('foo.conf', content=from_template('foo.conf.tpl'))

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
            return engine.get_template(name).render(context)

        return render_template

    yield tpl