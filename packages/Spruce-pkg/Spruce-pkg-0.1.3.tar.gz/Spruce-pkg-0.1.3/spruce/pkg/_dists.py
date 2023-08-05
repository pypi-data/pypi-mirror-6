"""Distribution packages."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import logging as _logging
import pkg_resources as _pkgr

from . import _dists_misc
from . import _envs
from . import _exc
from . import _misc
from . import _requirements


def dist_requirements_graph(dist, extras=(), env=None, update_cmd=None,
                            logger=None, loglevel=_logging.DEBUG):
    return _dist_requirements_graph(dist, extras=extras, env=env,
                                    update_cmd=update_cmd, logger=logger,
                                    loglevel=loglevel)


def dists_requirements_graph(dists, extras=False, env=None,
                             update_cmd=None, logger=None,
                             loglevel=_logging.DEBUG):
    return _dists_requirements_graph(dists, extras=extras, env=env,
                                     update_cmd=update_cmd, logger=logger,
                                     loglevel=loglevel)


def update_dist_metadata(dist, cmd, recursive=False, extras=False,
                         env=None, logger=None, loglevel=_logging.DEBUG):
    env = _envs.normalized_env(env, dists=(dist,))
    extras = _misc.normalized_extras(extras, env=env)
    env = _normalized_update_dist_metadata(dist, cmd=cmd, recursive=recursive,
                                           extras=extras, env=env,
                                           logger=logger, loglevel=loglevel)
    return env.map[_dists_misc.normalized_dist_name(dist)], env


def _dist_requirement_subgraph(requirement, extras, env, update_cmd, logger,
                               loglevel, subgraphs):

    for subgraph_requirement, subgraph_requirement_subgraph \
            in subgraphs.items():
        if requirement == subgraph_requirement:
            return subgraph_requirement_subgraph

    for env_dist in env:
        if env_dist in requirement:
            return _dist_requirements_graph(env_dist,
                                            extras=extras,
                                            env=env,
                                            update_cmd=update_cmd,
                                            logger=logger,
                                            loglevel=loglevel,
                                            subgraphs=subgraphs)

    return None


def _dist_requirements_graph(dist, extras, env, update_cmd, logger,
                             loglevel, subgraphs=None):

    if subgraphs is None:
        subgraphs = {}

    dist_name = _dists_misc.normalized_dist_name(dist)
    extras = _misc.normalized_extras(extras, env=env)
    dist_extras = extras.get(dist_name, ())
    dist_requirement = dist.as_requirement()
    dist_requirement.extras = dist_extras

    for subgraph_requirement, subgraph_requirement_subgraph \
            in subgraphs.items():
        if dist_requirement == subgraph_requirement:
            return {dist_requirement: subgraph_requirement_subgraph}

    logger.log(loglevel, 'constructing requirements graph for {}'.format(dist))

    if update_cmd:
        dist, env = update_dist_metadata(dist, cmd=update_cmd, env=env,
                                         logger=logger, loglevel=loglevel)

    dist_graph = {}
    for requirement in dist.requires(extras=dist_extras):
        requirement_subgraph = \
            _dist_requirement_subgraph(requirement,
                                       extras=extras,
                                       env=env,
                                       update_cmd=update_cmd,
                                       logger=logger,
                                       loglevel=loglevel,
                                       subgraphs=subgraphs)
        dist_graph[requirement] = requirement_subgraph
        subgraphs[requirement] = requirement_subgraph
    return {dist_requirement: dist_graph}


def _dists_requirements_graph(dists, extras, env, update_cmd, logger, loglevel,
                              subgraphs=None):

    env = _envs.normalized_env(env, dists=dists)
    if subgraphs is None:
        subgraphs = {}

    graph = {}
    for dist in dists:
        graph.update(_dist_requirements_graph(dist,
                                              extras=extras,
                                              env=env,
                                              update_cmd=update_cmd,
                                              logger=logger,
                                              loglevel=loglevel,
                                              subgraphs=subgraphs))
    return graph


def _normalized_update_dist_metadata(dist, cmd, recursive, extras, env, logger,
                                     loglevel):

    try:
        _misc.update_metadata_at(dist.location, cmd=cmd, logger=logger,
                                 loglevel=loglevel)
    except _exc.UpdateMetadataError as exc:
        raise _exc.UpdateDistMetadataError(dist, cmd, exc.message)

    dist_name = _dists_misc.normalized_dist_name(dist)
    found_dists_by_name = \
        {_dists_misc.normalized_dist_name(dist_): dist_
         for dist_ in _pkgr.find_distributions(dist.location)}

    try:
        dist = found_dists_by_name[dist_name]
    except KeyError:
        raise _exc.DistNotFound(name=dist_name, location=dist.location)
    env.map[dist_name] = dist

    if recursive:
        for requirement in dist.requires(extras=extras.get(dist_name, ())):
            requirement_name = \
                _requirements.normalized_requirement_name(requirement)
            try:
                child_dist = env.map[requirement_name]
            except KeyError:
                pass
            else:
                env = _normalized_update_dist_metadata(child_dist,
                                                       cmd=cmd,
                                                       recursive=True,
                                                       extras=extras,
                                                       env=env,
                                                       logger=logger,
                                                       loglevel=loglevel)

    return env
