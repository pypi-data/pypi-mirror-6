# coding: utf-8

""" Module-level imports for Spectroscopy Made Hard """

__author__ = "Andy Casey <andy@astrowizici.st>"

import logging

# Module specific imports
from session import Session
from utils import get_version

__all__ = ["Session", "__version__"]

__version__ = get_version()

# Initialise logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s: %(message)s',
                    datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)