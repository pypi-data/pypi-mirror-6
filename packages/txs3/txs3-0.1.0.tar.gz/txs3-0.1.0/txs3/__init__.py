"""
txs3, a Twisted based asynchronous interface to Amazon S3.

MIT License. See LICENSE for more details.
Copyright (c) 2014, Jonathan Stoppani
"""


from .api import Service
from .client import S3Client


__version__ = '0.1.0'
__url__ = 'https://github.com/GaretJax/txs3'
__all__ = ['Service', 'S3Client']
