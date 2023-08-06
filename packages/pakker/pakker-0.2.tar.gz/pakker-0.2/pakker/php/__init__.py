# encoding: utf-8

"""
    Functions for dealing with data that was serialized using PHP's
    `serialize()` function.
"""

from pakker.php._serialize import dump, dumps
from pakker.php._unserialize import loads


__all__ = ["dump", "dumps", "loads"]

