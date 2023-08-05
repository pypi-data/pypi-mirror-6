#!/usr/bin/env python

"""Find Python projects."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import argparse as _argparse
from functools import partial as _partial
import logging as _logging
import os as _os
import re as _re
import shlex as _shlex
import subprocess as _subprocess
import sys as _sys
import traceback as _traceback

import spruce.pkg as _pkg


def main(use_devel_projects=False):

    loglevel = _logging.WARNING
    _logger.setLevel(level=loglevel)
    _log_formatter = _logging.Formatter(_LOGGING_FORMAT)
    _log_handler = _logging.StreamHandler()
    _log_handler.setFormatter(_log_formatter)
    _logger.addHandler(_log_handler)

    try:
        args = _parse_args(use_devel_projects=use_devel_projects)

        loglevel = _LOGLEVELS_BY_ARGVALUE[args.loglevel]
        _logger.setLevel(loglevel)

        _run(args, use_devel_projects=use_devel_projects)

    except _CriticalError as exc:
        _logger.critical(_format_exc(exc))
        _sys.exit(1)
    except RuntimeError as exc:
        _logger.error(_format_exc(exc))
        _sys.exit(1)


def main_using_devel_projects():
    main(use_devel_projects=True)


def _format_exc(exc, limit=None):
    message = str(exc)
    if _logger.isEnabledFor(_logging.DEBUG):
        message += '\n' + _traceback.format_exc(limit=limit)
    return message


def _parse_args(use_devel_projects=False):

    description = 'Find Python projects.'

    parser = _argparse.ArgumentParser(description=description, add_help=False)

    dist_format_metavar = 'DIST_FORMAT'
    exec_cmd_metavar = 'EXEC_CMD'
    path_metavar = 'PATH'
    project_format_metavar = 'PROJECT_FORMAT'
    project_metavar = 'PROJECT'
    update_cmd_metavar = 'UPDATE_CMD'
    update_cmd_const = _UPDATE_CMD_DEFAULT_USING_DEVEL \
                           if use_devel_projects else _UPDATE_CMD_DEFAULT

    selection_group = parser.add_argument_group('selection')
    selection_group\
     .add_argument('projects',
                   metavar=project_metavar,
                   nargs='*',
                   help='list the specified projects (default: all of the'
                         ' projects found in each {path_metavar})'
                         .format(path_metavar=path_metavar))
    if use_devel_projects:
        selection_group\
         .add_argument('--no-require',
                       dest='require',
                       action='store_false',
                       help='do not require that each {project_metavar} is'
                             ' found'
                             .format(project_metavar=project_metavar))
    else:
        selection_group\
         .add_argument('--require', action='store_true',
                       help='require that each {project_metavar} is found'
                             .format(project_metavar=project_metavar))
    selection_group\
     .add_argument('-I',
                   '--include-deps',
                   action='store_true',
                   help='include the dependencies of each {project_metavar} in'
                         ' the result'
                         .format(project_metavar=project_metavar))
    selection_group\
     .add_argument('-O',
                   '--only-deps',
                   action='store_true',
                   help='include the dependencies of each {project_metavar}--'
                         'but not the {project_metavar} itself--in the result'
                         .format(project_metavar=project_metavar))
    if use_devel_projects:
        path_default_str = \
            'the set of subdirectories of {devel_src} and {devel_src_ext}'\
             ' that are specified in the corresponding'\
             ' {devel_projects_list_file} files'\
             .format(devel_src='$' + _pkg.DEVEL_SRC_ENVVAR,
                     devel_src_ext=
                         _os.path.join('$' + _pkg.DEVEL_SRC_ENVVAR,
                                       _pkg.DEVEL_SRC_EXT_DIR),
                     devel_projects_list_file=_pkg.DEVEL_PROJECTS_LIST_FILE)
    else:
        path_default_str = \
            'the current Python environment\'s module search path'
    selection_group\
     .add_argument('-P',
                   '--path',
                   metavar=path_metavar,
                   nargs='+',
                   help='search for Python projects in the specified'
                         ' directories; this is a list of paths; (default:'
                         ' {default_str})'
                         .format(default_str=path_default_str))
    if use_devel_projects:
        dists_relpaths_default = _pkg.DEVEL_PROJECTS_DISTS_RELPATHS
    else:
        dists_relpaths_default = _DISTS_RELPATHS_DEFAULT
    selection_group\
     .add_argument('--dists-relpaths',
                   default=_DISTS_RELPATHS_DEFAULT,
                   help='search for Python distribution packages in the'
                         ' specified paths relative to each {path_metavar}'
                         ' (default: {default!r})'
                         .format(default=dists_relpaths_default,
                                 path_metavar=path_metavar))
    selection_group\
     .add_argument('-U',
                   '--update',
                   dest='update_cmd',
                   metavar=update_cmd_metavar,
                   nargs='?',
                   const=update_cmd_const,
                   help='run {metavar} in each {path_metavar} prior to'
                         ' searching in it for distribution packages; by'
                         ' default, this step is omitted; if this option is'
                         ' used without an {metavar}, it defaults to {const!r}'
                         .format(metavar=update_cmd_metavar,
                                 const=update_cmd_const,
                                 path_metavar=path_metavar))
    selection_group\
     .add_argument('-D',
                   '--distinction',
                   choices=_DISTINCTION_CHOICES,
                   default=_DISTINCTION_DEFAULT,
                   help='distinguish between projects found in each'
                         ' {path_metavar} according to the specified criterion'
                         ' (default: {default!r})'
                         .format(default=_DISTINCTION_DEFAULT,
                                 path_metavar=path_metavar))
    selection_group\
     .add_argument('-E',
                   '--extras',
                   default=_EXTRAS_DEFAULT,
                   help='when identifying dependencies, consider those'
                         ' entailed by the specified extra features; this is'
                         ' either {value_all!r} (all extras), {value_none!r}'
                         ' (no extras), or a list of strings formatted like'
                         ' {value_specific_format!r} (the specified extras for'
                         ' the specified distribution packages) (default:'
                         ' {default!r})'
                           .format(value_all=_EXTRAS_ARGVALUE_ALL,
                                   value_none=_EXTRAS_ARGVALUE_NONE,
                                   value_specific_format=
                                       _EXTRAS_ARGVALUE_SPECIFIC_FORMAT,
                                   default=_EXTRAS_DEFAULT))

    presentation_group = parser.add_argument_group('presentation')
    format_placeholders_helps = \
        ('{name} is the project\'s name',
         '{location} is the project\'s location',
         '{{dists:DELIM}} are the project\'s distribution packages, each in'
          ' the format defined by {dist_format_metavar}, delimited by DELIM'
          .format(dist_format_metavar=dist_format_metavar),
         )
    format_placeholders_help = '; '.join(format_placeholders_helps)
    presentation_group\
     .add_argument('-F',
                   '--format',
                   metavar=project_format_metavar,
                   default=_PROJECT_FORMAT_DEFAULT,
                   help='format each project\'s string representation as'
                         ' specified; this is a string within which the'
                         ' following placeholders are defined:'
                         ' {placeholders_help} (default: {default!r})'
                         .format(metavar=project_format_metavar,
                                 default=_PROJECT_FORMAT_DEFAULT,
                                 placeholders_help=format_placeholders_help))
    dist_format_placeholders_helps = \
        ('{name} is the distribution\'s name',
         '{version} is the distribution\'s version',
         '{py_version} is the distribution\'s Python version',
         '{platform} is the distribution\'s platform',
         '{extras} are the distribution\'s extra features',
         '{location} is the distribution\'s location',
         '{precedence} is the distribution\'s precedence',
         )
    dist_format_placeholders_help = '; '.join(dist_format_placeholders_helps)
    presentation_group\
     .add_argument('--dist-format',
                   metavar=dist_format_metavar,
                   default=_DIST_FORMAT_DEFAULT,
                   help='format projects\' distribution packages as specified;'
                         ' this is a string within which the following'
                         ' placeholders have meaning: {placeholders_help}'
                         ' (default: {default!r})'
                         .format(default=_DIST_FORMAT_DEFAULT,
                                 placeholders_help=
                                     dist_format_placeholders_help))
    presentation_group.add_argument('-S', '--sort', choices=_SORT_CHOICES,
                                    help='sort on the specified property')
    presentation_group.add_argument('-R', '--reverse', action='store_true',
                                    help='reverse the order')

    action_group = parser.add_argument_group('actions')
    action_group\
     .add_argument('-p',
                   '--print',
                   dest='print_',
                   action='store_true',
                   help='print each project\'s string representation in the'
                         ' format defined by {project_format_metavar}'
                         .format(project_format_metavar=
                                     project_format_metavar))
    action_group\
     .add_argument('-e',
                   '--exec',
                   metavar=exec_cmd_metavar,
                   dest='exec_cmd',
                   help='execute the {metavar} on each project,'
                         ' substituting all occurrences of {{}} in {metavar}'
                         ' with the project\'s string representation in the'
                         ' format defined by {project_format_metavar}'
                         .format(metavar=exec_cmd_metavar,
                                 project_format_metavar=
                                     project_format_metavar))

    misc_group = parser.add_argument_group('miscellany')
    misc_group.add_argument('-h', '--help', action='store_true',
                            help='show this help message and exit')
    misc_group\
     .add_argument('--loglevel',
                   choices=sorted(_LOGLEVELS_BY_ARGVALUE.keys(),
                                  key=(lambda value:
                                           -_LOGLEVELS_BY_ARGVALUE[value])),
                   default=_LOGLEVEL_DEFAULT,
                   help='the logging level (default: {default!r})'
                         .format(default=_LOGLEVEL_DEFAULT))
    misc_group.add_argument('--quiet', dest='loglevel', action='store_const',
                            const='debug',
                            help='alias for \'--loglevel error\'')
    misc_group.add_argument('-v', '--verbose', dest='loglevel',
                            action='store_const', const='debug',
                            help='alias for \'--loglevel debug\'')

    args = parser.parse_args()

    if args.help:
        parser.print_help()
        _sys.exit()

    return args


def _run(args, use_devel_projects=False):

    if args.projects:
        names = args.projects
    else:
        names = True

    include_deps = args.include_deps or args.only_deps

    if args.extras == _EXTRAS_ARGVALUE_ALL:
        extras = True
    elif args.extras == _EXTRAS_ARGVALUE_NONE:
        extras = False
    else:
        extras = {}
        for dist_extras_str in extras:
            dist, dist_extras_str = dist_extras_str.split(':', 1)
            dist_extras = dist_extras_str.split(',')
            extras[dist] = dist_extras

    update_cmd = args.update_cmd

    if args.path is None and use_devel_projects:
        env_searchpaths = _pkg.devel_searchpaths()
        searchpaths = _pkg.devel_searchpaths(names,
                                             require=args.require,
                                             include_deps=include_deps,
                                             distinction=args.distinction,
                                             extras=extras,
                                             update_cmd=update_cmd,
                                             logger=_logger)
        update_cmd = None

    else:
        env_searchpaths = args.path
        searchpaths = env_searchpaths

    actions = []
    if args.print_:
        actions.append(_partial(print_project, format=args.format,
                                dist_format=args.dist_format))
    if args.exec_cmd is not None:
        actions.append(_partial(exec_project, args.exec_cmd,
                                format=args.format,
                                dist_format=args.dist_format))
    if not actions:
        actions.append(_partial(print_project, format=args.format,
                                dist_format=args.dist_format))

    projects = _pkg.find_projects(names,
                                  require=args.require,
                                  include_deps=include_deps,
                                  searchpaths=searchpaths,
                                  dists_relpaths=args.dists_relpaths,
                                  distinction=args.distinction,
                                  extras=extras,
                                  update_cmd=update_cmd,
                                  logger=_logger)

    if args.sort == 'deps':
        if update_cmd:
            searchpaths_set = set(searchpaths)
            for path in env_searchpaths:
                if path not in searchpaths_set:
                    _pkg.update_metadata_at(path, cmd=update_cmd,
                                            logger=_logger)

        env_projects = _pkg.find_projects(searchpaths=env_searchpaths,
                                          dists_relpaths=args.dists_relpaths,
                                          distinction=args.distinction)
        env = _pkg.DistEnv(_pkg.projects_dists(env_projects))
        projects = _pkg.projects_sorted_by_requirements\
                    (projects, include_deps=include_deps, extras=extras,
                     env=env, logger=_logger)

    if args.reverse:
        projects = reversed(projects)

    for project in projects:
        if args.only_deps and project.name in names:
            continue

        for action in actions:
            action(project)


def dist_str(dist, format):
    format_dict = {placeholder: getattr(dist, property_)
                   for placeholder, property_
                   in _DIST_FORMAT_PROPERTIES_BY_PLACEHOLDER.items()}
    return format.format(**format_dict)


def exec_project(cmd, project, format, dist_format):

    project_str_ = project_str(project, format=format, dist_format=dist_format)
    project_cmd = cmd.replace('{}', project_str_)

    project_dir = project.location

    _logger.debug('project {} at {!r}: executing {!r}'
                   .format(project.name, project_dir, cmd))
    try:
        debug_output = _subprocess.check_output(_shlex.split(project_cmd),
                                                cwd=project_dir,
                                                stderr=_subprocess.STDOUT)
    except _subprocess.CalledProcessError as exc:
        raise _CriticalError('error executing {!r} in {!r}:\n{}'
                              .format(project_cmd, project_dir, exc.output)), \
              None, _sys.exc_info()[2]
    for line in debug_output.split('\n'):
        _logger.debug(line)


def project_deps_iter(project, extras, env):
    project_name = _pkg.normalized_project_name(project)
    for requirement in project.requirements(extras=extras.get(project_name,
                                                              ())):
        try:
            required_project = _pkg.Project.from_requirement(requirement,
                                                             env=env)
        except _pkg.DistNotFound:
            pass
        else:
            yield required_project
            for required_project in project_deps_iter(required_project,
                                                      extras=extras, env=env):
                yield required_project


def print_project(project, format, dist_format, file=_sys.stdout):
    print >> file, project_str(project, format=format, dist_format=dist_format)


def project_str(project, format, dist_format):
    project_format = format[:]
    format_dists_match = \
        _PROJECT_FORMAT_DISTS_PATTERN_ATOM.search(project_format)
    if format_dists_match:
        delim = format_dists_match.group('delim')
        project_format = \
            _re.sub(_PROJECT_FORMAT_DISTS_PATTERN_ATOM,
                    delim.join(dist_str(dist, format=dist_format)
                               for dist in project.dists),
                    project_format)
    format_dict = {'location': project.location, 'name': project.name}
    return project_format.format(**format_dict)


class _CriticalError(RuntimeError):
    """
    An exception after which it is unsafe or not useful to continue running
    the application.

    .. note:: **TODO:** generalize and migrate

    """
    pass


_DISTINCTION_CHOICES = ('dist', 'path')

_DISTINCTION_DEFAULT = 'dist'


_DISTS_RELPATHS_DEFAULT = ('.',)


_EXTRAS_ARGVALUE_ALL = '+'

_EXTRAS_ARGVALUE_NONE = '-'

_EXTRAS_ARGVALUE_SPECIFIC_FORMAT = 'dist0:extra0,extra1'

_EXTRAS_DEFAULT = _EXTRAS_ARGVALUE_ALL


_SORT_CHOICES = ('deps',)


_PROJECT_FORMAT_DEFAULT = '{name}'

_PROJECT_FORMAT_DISTS_PATTERN_ATOM = _re.compile(r'\{dists:(?P<delim>[^}]*)\}')

_DIST_FORMAT_PROPERTIES_BY_PLACEHOLDER = \
    {'name': 'project_name', 'version': 'version', 'py_version': 'py_version',
     'platform': 'platform', 'extras': 'extras', 'location': 'location',
     'precedence': 'precedence'}

_DIST_FORMAT_DEFAULT = '{name} {version} ({location})'


_UPDATE_CMD_DEFAULT = _pkg.UPDATE_PROJECT_METADATA_CMD

_UPDATE_CMD_DEFAULT_USING_DEVEL = _pkg.UPDATE_DEVEL_PROJECT_METADATA_CMD


_logger = _logging.getLogger()

_LOGGING_FORMAT = '%(levelname)s: %(message)s'

_LOGLEVELS_BY_ARGVALUE = {'critical': _logging.CRITICAL,
                          'error': _logging.ERROR,
                          'warning': _logging.WARNING,
                          'info': _logging.INFO,
                          'debug': _logging.DEBUG,
                          }

_LOGLEVEL_DEFAULT = 'warning'


if __name__ == '__main__':
    main()
