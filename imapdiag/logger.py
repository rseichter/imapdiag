"""
This file is part of "imapdiag".

Copyright © 2020 Ralph Seichter
"""
from logging import Logger
from logging import basicConfig
from logging import getLogger

from imapdiag import PROGRAM

_logger = None


def get_logger(level: str = 'DEBUG') -> Logger:
    global _logger
    if _logger is None:
        basicConfig(level=level.upper(), format='%(message)s')
        _logger = getLogger(PROGRAM)
    return _logger
