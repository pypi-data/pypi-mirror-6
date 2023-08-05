"""Conventions."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from itertools import chain as _chain
import logging as _logging
import os as _os
import re as _re

from . import _envs
from . import _exc
from . import _misc
from . import _projects
from . import _projects_misc
from . import _requirements


DEVEL_SRC_ENVVAR = 'SRC'
"""
An environment variable whose value is a path to the root directory of
the standard in-development projects.

"""

DEVEL_SRC_EXT_DIR = 'ext'
"""
A path to the root directory of the standard externally sourced
in-development projects.

This path is resolved relative to :code:`os.environ[DEVEL_SRC_ENVVAR]`.

"""

DEVEL_PROJECTS_DISTS_RELPATHS = ('.', 'src',)
"""
Relative paths at which a standard in-development project's distribution
packages might be found.

The paths are relative to each project's root.

"""

DEVEL_PROJECTS_LIST_FILE = _os.path.join('.projinfo', 'projects-python-dist')
"""A path to the file that lists the standard in-development projects.

This path is resolved relative to :code:`os.environ[DEVEL_SRC_ENVVAR]`
or :code:`os.path.join(os.environ[DEVEL_SRC_ENVVAR],
DEVEL_SRC_EXT_DIR)`.

"""

STD_PROJECT_PREFIXES = ('spruce-',)
"""
Prefixes that are commonly omitted from standard projects' names in some
situations.

"""

UPDATE_DEVEL_PROJECT_METADATA_CMD = 'make clean egginfo'
"""
The standard command to update a standard in-development project's
metadata.

"""


def devel_ext_projects(**kwargs):
    """

    .. seealso:: :func:`devel_ext_projects_iter`

    """
    return list(devel_ext_projects_iter(**kwargs))


def devel_ext_projects_iter(**kwargs):
    """

    .. seealso:: :func:`~spruce.pkg._projects.find_projects_iter`

    """
    return _projects.find_projects_iter(devel_searchpaths_iter
                                            (src=devel_src_ext()), **kwargs)


def devel_project_canon_dirname(name):
    return _re.sub(r'^{}'.format('|'.join(STD_PROJECT_PREFIXES)), '', name)


def devel_projects(**kwargs):
    """

    .. seealso:: :func:`devel_projects_iter`

    """
    return list(devel_projects_iter(**kwargs))


def devel_projects_dirnames(**kwargs):
    """

    .. seealso:: :func:`devel_projects_dirnames_iter`

    """
    return list(devel_projects_dirnames_iter(**kwargs))


def devel_projects_dirnames_iter(src=None,
                                 projects_list_file=DEVEL_PROJECTS_LIST_FILE):

    if src is None:
        src = devel_src()

    with open(_os.path.join(src, DEVEL_PROJECTS_LIST_FILE)) as file_:
        return (line.strip() for line in file_.readlines())


def devel_projects_iter(**kwargs):
    """

    .. seealso:: :func:`~spruce.pkg._projects.find_projects_iter`

    """
    return _projects.find_projects_iter(devel_searchpaths_iter(), **kwargs)


def devel_searchpaths(*args, **kwargs):
    """

    .. seealso:: :func:`devel_searchpaths_iter`

    """
    return list(devel_searchpaths_iter(*args, **kwargs))


def devel_searchpaths_iter(names=True,
                           src=None,
                           ext_dir=DEVEL_SRC_EXT_DIR,
                           require=False,
                           include_deps=False,
                           distinction='dist',
                           extras=False,
                           update_cmd=None,
                           logger=None,
                           loglevel=_logging.DEBUG):

    if src is None:
        src = devel_src()
    srcs = [src]
    if ext_dir is not None:
        srcs.append(_os.path.join(src, ext_dir))

    if names is True:
        for path in _chain(*([_os.path.join(src_, dirname)
                              for dirname
                              in devel_projects_dirnames_iter(src=src_)]
                             for src_ in srcs)):
            if update_cmd:
                _misc.update_metadata_at(path, cmd=update_cmd, logger=logger,
                                         loglevel=loglevel)

            yield path
        return

    for path in _devel_searchpaths_iter(names,
                                        srcs=srcs,
                                        require=require,
                                        include_deps=include_deps,
                                        distinction=distinction,
                                        extras=extras,
                                        update_cmd=update_cmd,
                                        logger=logger,
                                        loglevel=loglevel):
        yield path


def devel_src(envvar=DEVEL_SRC_ENVVAR):
    return _os.environ[DEVEL_SRC_ENVVAR]


def devel_src_ext(ext_dir=DEVEL_SRC_EXT_DIR):
    return _os.path.join(devel_src(), DEVEL_SRC_EXT_DIR)


def update_devel_dist_metadata(dist, **kwargs):
    """

    .. seealso:: :func:`~spruce.pkg._misc.update_dist_metadata`

    """
    return _misc.update_dist_metadata(dist,
                                      cmd=UPDATE_DEVEL_PROJECT_METADATA_CMD,
                                      **kwargs)


_DEVEL_PROJECT_DIRNAME_PATTERN_FORMAT = \
    r'{}[\d\.\-_]*(?:[abcr]|alpha|beta|rc|dev[\d\.\-_]*)?'


def _devel_project_dirname_match(name, dirname):
    canon_dirname = devel_project_canon_dirname(name)
    return _re.match(_DEVEL_PROJECT_DIRNAME_PATTERN_FORMAT
                      .format(canon_dirname),
                     dirname, _re.IGNORECASE)


def _devel_project_searchpaths_iter(name, src):
    for dirname in _os.listdir(src):
        if _devel_project_dirname_match(name, dirname):
            dirpath = _os.path.join(src, dirname)
            if _project_at_path(dirpath):
                yield dirpath


def _devel_searchpaths_iter(names,
                            srcs,
                            require=False,
                            include_deps=False,
                            distinction='dist',
                            extras=False,
                            update_cmd=None,
                            seen_paths=None,
                            logger=None,
                            loglevel=_logging.DEBUG):

    if seen_paths is None:
        seen_paths = set()

    missing_names = []
    for name in names:
        name = _projects_misc.normalized_project_name(name)

        path = None
        for path in _chain(*(_devel_project_searchpaths_iter(name, src=src)
                             for src in srcs)):
            if path in seen_paths:
                continue
            seen_paths.add(path)

            if update_cmd:
                _misc.update_metadata_at(path, cmd=update_cmd, logger=logger,
                                         loglevel=loglevel)

            yield path

            if include_deps:
                project = _projects.Project.from_path(path)
                env = _envs.DistEnv(project.dists)
                project_extras = \
                    _misc.normalized_extras(extras, env=env).get(name, ())
                requirements_names = \
                    (_requirements.normalized_requirement_name(requirement)
                     for requirement
                     in project.requirements(extras=project_extras))
                for dep_path \
                        in _devel_searchpaths_iter(requirements_names,
                                                   srcs=srcs,
                                                   require=False,
                                                   include_deps=include_deps,
                                                   distinction=distinction,
                                                   extras=extras,
                                                   update_cmd=update_cmd,
                                                   logger=logger,
                                                   loglevel=loglevel,
                                                   seen_paths=seen_paths):
                    yield dep_path

        if path is None:
            missing_names.append(name)
            continue

    if require and missing_names:
        tried_paths = list(_devel_searchpaths_iter(missing_names, srcs=srcs))
        raise _exc.ProjectsNotFound(missing_names, tried_paths)


def _project_at_path(path):
    try:
        return _projects.Project.from_path(path)
    except _exc.DistNotFound:
        return None
