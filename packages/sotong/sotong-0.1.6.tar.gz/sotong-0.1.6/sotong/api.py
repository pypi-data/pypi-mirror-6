"""
API module

.. autosummary::

    Sotong
    cd
    shell
    alert
    logger
"""
import os

from fabric.api import local, lcd, settings



cd = lcd

__all__ = ['Sotong', 'cd', 'shell', 'alert', 'logger']
