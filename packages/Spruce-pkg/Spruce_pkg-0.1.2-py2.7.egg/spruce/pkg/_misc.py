"""Packaging miscellany."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import logging as _logging
import shlex as _shlex
import subprocess as _subprocess
import sys as _sys

from . import _dists_misc
from . import _exc


UPDATE_PROJECT_METADATA_CMD = _sys.executable + ' setup.py egg_info'
"""The default command to update a project's metadata."""


def normalized_extras(extras, env):
    if extras is True:
        return {_dists_misc.normalized_dist_name(dist): dist.extras
                for dist in env}
    elif extras is False:
        return {}
    else:
        return extras


def update_metadata_at(location, cmd, logger=None, loglevel=_logging.DEBUG):

    if logger:
        logger.log(loglevel,
                   'updating metadata at {!r} using {!r}'.format(location,
                                                                 cmd))
    try:
        debug_output = _subprocess.check_output(_shlex.split(cmd),
                                                cwd=location,
                                                stderr=_subprocess.STDOUT)
    except _subprocess.CalledProcessError as exc:
        raise _exc.UpdateMetadataError(location, cmd, exc.output)
    if logger:
        for line in debug_output.split('\n'):
            logger.log(loglevel, line)
