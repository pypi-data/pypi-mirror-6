"""Cockatoo: A similarity metric for macromolecular crystallization conditions."""
# :copyright: (c) 2013 Andrew E. Bruno
# :license:   GPL v3, see LICENSE for more details.

VERSION = (0, 0, 1)
__version__ = ".".join(map(str, VERSION[:]))

from cockatoo import screen,c6,metric
