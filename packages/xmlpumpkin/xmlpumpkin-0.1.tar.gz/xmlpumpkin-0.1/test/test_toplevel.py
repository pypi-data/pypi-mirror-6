# encoding: utf-8

from attest import Tests
import xmlpumpkin
from .test_runner import Fixtures


pkg_unit = Tests()


@pkg_unit.test
def runnerfromtop():
    """cabocha runner is accessible from pkg top?"""
    from xmlpumpkin import cabocha

@pkg_unit.test
def treefromtop():
    """Tree is accessible from pkg top?"""
    from xmlpumpkin import Tree

@pkg_unit.test
def parse():
    for key in Fixtures.texts:
        text = Fixtures.texts[key]

        tree = xmlpumpkin.parse_to_tree(text)
        assert isinstance(tree, xmlpumpkin.Tree)
