"""Requirements."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from collections \
    import MutableSet as _MutableSet, namedtuple as _namedtuple, Set as _Set
from itertools import chain as _chain
from operator import attrgetter as _attrgetter
import pkg_resources as _pkgr

from . import _exc


def normalized_requirement_name(requirement):
    try:
        name = requirement.project_name
    except AttributeError:
        name = requirement
    return Requirement(name.lower()).project_name


def flattened_requirements_graph(graph, reverse=False):
    flattened_requirements = []
    for reqgraphinfo in sorted(_requirements_graph_reqgraphinfo(graph,
                                                                depth=0),
                               key=_attrgetter('maxdepth'),
                               reverse=(not reverse)):
        intersection = requirements_intersection(*reqgraphinfo.atoms)

        assert len(intersection) <= 1
        if len(intersection) == 0:
            raise _exc.IncompatibleRequirements(reqgraphinfo.atoms)

        flattened_requirements.append(intersection[0])
    return flattened_requirements


def project_in_requirements_graph(project, graph):

    try:
        name = project.name
    except AttributeError:
        name = project
    name = name.lower()

    return _normalized_project_in_requirements_graph(name, graph)


def require_requirement_isvalid(requirement):
    for spec in requirement.specs:
        for other_spec in requirement.specs:
            if not requirement_specs_compatible(spec, other_spec):
                raise _exc.InconsistentRequirementSpecs(requirement,
                                                        (spec, other_spec))


def requirement_atoms(requirement):
    if requirement.specs:
        return tuple(Requirement(requirement.project_name, [spec],
                                 requirement.extras)
                     for spec in requirement.specs)
    else:
        return (requirement,)


def requirement_isvalid(requirement):
    try:
        require_requirement_isvalid(requirement)
    except _exc.InconsistentRequirementSpecs:
        return False
    else:
        return True


def requirement_specs_compatible(spec1, spec2):

    op1, version1 = spec1
    op2, version2 = spec2

    if op1 == '==':
        if op2 == '==':
            return version1 == version2
        elif op2 == '!=':
            return version1 != version2
    elif op1 == '!=':
        if op2 == '==':
            return version1 != version2
    elif op1 == '<':
        if op2 in ('>', '>='):
            return version1 in _pkgr.Requirement('', [('>', version2)], ())
    elif op1 == '<=':
        if op2 in ('>', '>='):
            return version1 in _pkgr.Requirement('', [(op2, version2)], ())
    elif op1 == '>':
        if op2 in ('<', '<='):
            return version1 in _pkgr.Requirement('', [('<', version2)], ())
    elif op1 == '>=':
        if op2 in ('<', '<='):
            return version1 in _pkgr.Requirement('', [(op2, version2)], ())
    return True


def requirements_compatible(requirement1, requirement2):
    return len(requirements_intersection(requirement1, requirement2)) > 0


# TODO: (Python 3)
#def requirements_intersection(*requirements, validate=True):
def requirements_intersection(*requirements, **kwargs):

    validate = kwargs.get('validate', True)

    intersections_by_name = {}

    for requirement in requirements:
        name = normalized_requirement_name(requirement)

        try:
            prev_intersection = intersections_by_name[name]
        except KeyError:
            intersections_by_name[name] = requirement
        else:
            if prev_intersection is None:
                continue

            intersection_extras = set(prev_intersection.extras) \
                                  | set(requirement.extras)
            intersection_specs = set(prev_intersection.specs) \
                                 | set(requirement.specs)
            intersection = Requirement(name, intersection_specs,
                                       intersection_extras)

            if validate and not requirement_isvalid(intersection):
                intersection = None

            intersections_by_name[name] = intersection

    return [intersection for intersection in intersections_by_name.values()
            if intersection is not None]


class RequirementSetABC(object):

    def __init__(self, items=()):

        self._items_by_name = {}

        for item in items:
            self._add(item)

    def __contains__(self, item):

        name = normalized_requirement_name(item)

        try:
            prev_items = self._items_by_name[name]
        except KeyError:
            return False

        return all(item in prev_item for prev_item in prev_items)

    def __iter__(self):
        return _chain(*self._items_by_name.values())

    def __len__(self):
        return sum(len(atoms) for atoms in self._items_by_name.itervalues())

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, tuple(iter(self)))

    def _add(self, item):

        require_requirement_isvalid(item)

        name = normalized_requirement_name(item)
        item_atoms = requirement_atoms(item)

        try:
            prev_items = self._items_by_name[name]
        except KeyError:
            new_atoms = set(item_atoms)
        else:
            for item_atom in item_atoms:
                for prev_item in prev_items:
                    if not requirements_compatible(item_atom, prev_item):
                        message = 'incompatible specs {}'\
                                   .format(sorted(set(item_atom.specs)
                                                  | set(prev_item.specs)))
                        raise _exc.IncompatibleRequirements((item, prev_item),
                                                            message)

            intersection = requirements_intersection(item, *prev_items)

            assert len(intersection) <= 1
            if len(intersection) == 0:
                raise _exc.IncompatibleRequirements((item, prev_item))

            new_atoms = set(requirement_atoms(intersection[0]))

        self._items_by_name[name] = new_atoms


class FrozenRequirementSet(RequirementSetABC, _Set):
    def __hash__(self):
        return hash(tuple(self._items_by_name.values()))


def Requirement(name, specs=(), extras=()):
    return _pkgr.Requirement.parse('{}[{}]{}'
                                    .format(name,
                                            ','.join(extras),
                                            ','.join('{}{}'.format(op, version)
                                                     for op, version
                                                     in specs)))


class RequirementSet(RequirementSetABC, _MutableSet):

    def add(self, item):
        self._add(item)

    def discard(self, item):

        name = normalized_requirement_name(item)

        try:
            project_items = self._items_by_name[name]
        except KeyError:
            pass
        else:
            project_items -= frozenset(requirement_atoms(item))


def _normalized_project_in_requirements_graph(name, graph):
    for requirement, requirement_subgraph in graph.items():
        if normalized_requirement_name(requirement) == name \
               or _normalized_project_in_requirements_graph\
                   (name, requirement_subgraph):
            return True
    return False


def _requirements_graph_reqgraphinfo(graph, depth):

    reqgraphinfo_by_name = {}

    def update_reqgraphinfo_by_name(reqgraphinfo):
        name = normalized_requirement_name(reqgraphinfo.project_name)
        try:
            prev_reqgraphinfo = reqgraphinfo_by_name[name]
        except KeyError:
            pass
        else:
            reqgraphinfo = \
                _RequirementGraphInfo(project_name=name,
                                      atoms=(prev_reqgraphinfo.atoms
                                             | reqgraphinfo.atoms),
                                      maxdepth=max(prev_reqgraphinfo.maxdepth,
                                                   reqgraphinfo.maxdepth))
        reqgraphinfo_by_name[name] = reqgraphinfo

    def update_reqgraphinfo_by_name_with_requirement(requirement, depth):
        reqgraphinfo = \
            _RequirementGraphInfo(project_name=requirement.project_name,
                                  atoms=RequirementSet((requirement,)),
                                  maxdepth=depth)
        update_reqgraphinfo_by_name(reqgraphinfo)

    for requirement in graph:
        update_reqgraphinfo_by_name_with_requirement(requirement, depth=depth)

        requirement_subgraph = graph[requirement]
        if requirement_subgraph is not None:
            child_depth = depth + 1
            for child_reqgraphinfo \
                    in _requirements_graph_reqgraphinfo(requirement_subgraph,
                                                        depth=child_depth):
                update_reqgraphinfo_by_name(child_reqgraphinfo)

    return reqgraphinfo_by_name.values()


class _RequirementGraphInfo(_namedtuple('_RequirementGraphInfo',
                                        ('project_name', 'atoms',
                                         'maxdepth'))):
    pass
