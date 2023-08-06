"""
peasel
"""

import contextlib
import os
import tempfile

from .ceasel import *

__version__ = '0.2.0'

@contextlib.contextmanager
def temp_ssi(file_path, sq_format=FMT_UNKNOWN, **kwargs):
    """
    Context manager.

    Create a temporary sequence index for the duration of the context manager.

    :param file_path: Path to sequence file
    :param sq_format: One of ``FMT_FASTA``, ``FMT_UNKNOWN``
    :param kwargs: Additional arguments to pass to ``tempfile.NamedTemporaryFile``
    :returns: Yields an instance of :class:`EaselSequenceIndex`
    """
    kwargs['delete'] = True
    if 'prefix' not in kwargs:
        kwargs['prefix'] = 'peasel-'
    if 'suffix' not in kwargs:
        kwargs['suffix'] = '.ssi'
    with tempfile.NamedTemporaryFile(**kwargs) as tf:
        tf.close()
        try:
            create_ssi(file_path, tf.name, sq_format)
            yield open_ssi(file_path, tf.name, sq_format)
        finally:
            os.unlink(tf.name)
