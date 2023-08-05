"""Projects."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from itertools import chain as _chain
import logging as _logging
import os as _os
import pkg_resources as _pkgr
import sys as _sys

from . import _dists
from . import _dists_misc
from . import _envs
from . import _exc
from . import _misc
from . import _projects_misc
from . import _requirements


def find_projects(*args, **kwargs):
    """

    .. seealso:: :func:`find_projects_iter`

    """
    return list(find_projects_iter(*args, **kwargs))


def find_projects_iter(names=True,
                       searchpaths=None,
                       require=False,
                       include_deps=True,
                       dists_relpaths=('.',),
                       distinction='dist',
                       extras=False,
                       update_cmd=None,
                       logger=None,
                       loglevel=_logging.DEBUG):

    if searchpaths is None:
        searchpaths = _sys.path

    if include_deps:
        return _find_projects_including_deps_iter(names,
                                                  searchpaths,
                                                  require=require,
                                                  dists_relpaths=
                                                      dists_relpaths,
                                                  distinction=distinction,
                                                  extras=extras,
                                                  update_cmd=update_cmd,
                                                  logger=logger,
                                                  loglevel=loglevel)
    else:
        return _find_projects_iter(names,
                                   searchpaths,
                                   require=require,
                                   distinction=distinction,
                                   update_cmd=update_cmd,
                                   logger=logger,
                                   loglevel=loglevel)


def projects_dists(projects):
    """

    .. seealso:: :func:`projects_dists_iter`

    """
    return list(projects_dists_iter(projects))


def projects_dists_iter(projects):
    return _chain(*(project.dists for project in projects))


def projects_sorted_by_requirements(*args, **kwargs):
    """

    .. seealso:: :func:`projects_sorted_by_requirements_iter`

    """
    return list(projects_sorted_by_requirements_iter(*args, **kwargs))


def projects_sorted_by_requirements_iter(projects,
                                         include_deps=False,
                                         extras=False,
                                         env=None,
                                         update_cmd=None,
                                         reverse=False,
                                         logger=None,
                                         loglevel=_logging.DEBUG):

    dists = projects_dists(projects)
    env = _envs.normalized_env(env, dists=dists)
    extras = _misc.normalized_extras(extras, env=env)

    graph = _dists.dists_requirements_graph(dists,
                                            extras=extras,
                                            env=env,
                                            update_cmd=update_cmd,
                                            logger=logger,
                                            loglevel=loglevel)

    projects_by_name = \
        {_projects_misc.normalized_project_name(project): project
         for project in projects}
    for requirement \
            in _requirements.flattened_requirements_graph(graph,
                                                          reverse=reverse):
        name = _requirements.normalized_requirement_name(requirement)
        try:
            yield projects_by_name[name]
        except KeyError:
            if include_deps:
                try:
                    dist = env.map[name]
                except _exc.DistNotFound:
                    pass
                else:
                    yield Project.from_dist(dist)


class Project(object):

    def __init__(self, name, dists=(), location=None):
        self._dists = list(dists)
        self._location = location
        self._name = name

    def __eq__(self, other):
        return self.name == other.name \
               and self.dists == other.dists

    def __repr__(self):
        return '{}({!r}, {!r})'.format(self.__class__.__name__, self.name,
                                       [_dists_misc.dist_repr(dist)
                                        for dist in self.dists])

    def __str__(self):
        return '{} {}'.format(self.name, self.dists)

    @property
    def dists(self):
        return self._dists

    @property
    def extras(self):
        return set(_chain(*(dist.extras for dist in self.dists)))

    @classmethod
    def from_dist(cls, dist, name=None):

        if name is None:
            name = dist.project_name

        return cls(name, (dist,))

    @classmethod
    def from_name(cls, name, env, new_name=None):
        return cls.from_dist(env.map[name], name=new_name)

    @classmethod
    def from_path(cls, path, name=None, dists_relpaths=('.',)):

        dists_paths = [_os.path.join(path, dists_relpath)
                       for dists_relpath in dists_relpaths]
        dists = list(_chain(*(_pkgr.find_distributions(dists_path, only=True)
                              for dists_path in dists_paths)))

        if not dists:
            raise _exc.DistNotFound(location=dists_paths)

        if name is None:
            name = dists[0].project_name

        return cls(name, dists, location=path)

    @classmethod
    def from_requirement(cls, requirement, env, name=None):
        requirement_name = \
            _requirements.normalized_requirement_name(requirement)
        return cls.from_name(requirement_name, env=env, new_name=name)

    @property
    def location(self):

        if self._location is not None:
            return self._location

        if not self.dists:
            raise _exc.NoDefinitiveProjectLocation(self,
                                                   'no distribution packages')

        dist_locations = {dist.location for dist in self.dists}

        if len(dist_locations) > 1:
            raise _exc.NoDefinitiveProjectLocation\
                   (self,
                    'multiple locations {}'
                     .format(tuple(sorted(dist_locations))))

        return iter(dist_locations).next()

    @property
    def name(self):
        return self._name

    def requirements(self, extras=()):
        return set(_chain(*(dist.requires(extras=extras)
                            for dist in self.dists)))


def _find_projects_including_deps_iter(names=True,
                                       searchpaths=None,
                                       require=False,
                                       dists_relpaths=('.',),
                                       distinction='dist',
                                       extras=True,
                                       update_cmd=None,
                                       logger=None,
                                       loglevel=_logging.DEBUG):

    found_projects = \
        list(_find_projects_unfiltered_iter(searchpaths,
                                            dists_relpaths=dists_relpaths,
                                            distinction=distinction,
                                            update_cmd=update_cmd,
                                            logger=logger,
                                            loglevel=loglevel))

    if names is True:
        for project in found_projects:
            yield project
        return

    found_env = _envs.DistEnv(projects_dists(found_projects))
    extras = _misc.normalized_extras(extras, env=found_env)
    found_projects_by_name = \
        {_projects_misc.normalized_project_name(project): project
         for project in found_projects}

    projects_including_deps = []
    missing_names = []
    for name in names:
        projects_including_deps.append(name)
        try:
            project = found_projects_by_name[name]
        except KeyError:
            if require:
                missing_names.append(name)
        else:
            yield project

            for requirement \
                    in project.requirements(extras=extras.get(project, ())):
                requirement_name = \
                    _requirements.normalized_requirement_name(requirement)
                try:
                    yield found_projects_by_name[requirement_name]
                except KeyError:
                    pass

    if missing_names:
        raise _exc.ProjectsNotFound(missing_names, searchpaths)


def _find_projects_iter(names=True, searchpaths=None, require=False,
                        dists_relpaths=('.',), distinction='dist',
                        update_cmd=None, logger=None, loglevel=_logging.DEBUG):

    found_projects = _find_projects_unfiltered_iter(searchpaths,
                                                    dists_relpaths=
                                                        dists_relpaths,
                                                    distinction=distinction,
                                                    update_cmd=update_cmd,
                                                    logger=logger,
                                                    loglevel=loglevel)

    if names is True:
        for project in found_projects:
            yield project
        return

    found_projects_by_name = {project.name: project
                              for project in found_projects}
    missing_names = []
    for name in names:
        try:
            yield found_projects_by_name[name]
        except KeyError:
            missing_names.append(name)

    if missing_names:
        raise _exc.ProjectsNotFound(missing_names, searchpaths)


def _find_projects_unfiltered_iter(searchpaths=None, dists_relpaths=('.',),
                                   distinction='dist', update_cmd=None,
                                   logger=None, loglevel=_logging.DEBUG):

    for path in searchpaths:
        if not _os.path.exists(path):
            continue

        if update_cmd:
            _misc.update_metadata_at(path, cmd=update_cmd, logger=logger,
                                     loglevel=loglevel)

        if distinction == 'path':
            try:
                yield Project.from_path(path, dists_relpaths=dists_relpaths)
            except _exc.DistNotFound:
                pass

        elif distinction == 'dist':
            for dists_relpath in dists_relpaths:
                dists_path = _os.path.join(path, dists_relpath)
                for dist in _pkgr.find_distributions(dists_path, only=True):
                    try:
                        yield Project.from_dist(dist)
                    except _exc.DistNotFound:
                        pass

        else:
            raise ValueError('invalid project distinction criterion {!r}'
                              .format(distinction))
