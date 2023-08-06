from argparse import ArgumentParser
from pywizard.cli import build_argparser


def test_cli():

    parser = build_argparser()
    assert isinstance(parser, ArgumentParser)