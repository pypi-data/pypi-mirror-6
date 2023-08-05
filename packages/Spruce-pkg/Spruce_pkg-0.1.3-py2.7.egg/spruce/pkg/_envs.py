"""Distribution package environments."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import abc as _abc
from collections \
    import Mapping as _Mapping, MutableMapping as _MutableMapping, \
           MutableSequence as _MutableSequence, Sequence as _Sequence

from . import _dists_misc
from . import _exc


def normalized_env(env, dists=()):
    if env is None or not isinstance(env, DistEnv):
        env = DistEnv(env)
    env.extend(dists)
    return env


class DistEnvABC(_Sequence):

    __metaclass__ = _abc.ABCMeta

    def __init__(self, dists=()):

        self._dists = []
        self._map = self._map_class()(self)

        for dist in dists:
            self._append(dist)

    def __contains__(self, item):
        return item in self._dists

    def __getitem__(self, key):
        return self._dists[key]

    def __iter__(self):
        return iter(self._dists)

    def __len__(self):
        return len(self._dists)

    def __repr__(self):
        return '{}({!r})'.format(self.__class__.__name__,
                                 [_dists_misc.dist_repr(dist)
                                  for dist in self._dists])

    @property
    def map(self):
        return self._map

    def _append(self, dist):
        self._dists.append(dist)
        self.map._dict[_dists_misc.normalized_dist_name(dist)] = dist

    @classmethod
    @_abc.abstractmethod
    def _map_class(cls):
        pass


class DistEnv(DistEnvABC, _MutableSequence):

    def __delitem__(self, key):
        del self._dists[key]

    def __setitem__(self, key, value):
        self._dists[key] = value

    def append(self, value):
        self._append(value)

    def extend(self, values):
        for value in values:
            self._append(value)

    def insert(self, key, value):

        self._dists.insert(key, value)

        name = _dists_misc.normalized_dist_name(value)
        if any(_dists_misc.normalized_dist_name(later_dist) == name
               for later_dist in self._dists[(key + 1):]):
            self._map._dict[name] = value

    @classmethod
    def _map_class(cls):
        return DistEnvMap


class FrozenDistEnv(DistEnvABC):

    def __init__(self, dists=()):
        super(FrozenDistEnv, self).__init__(dists)
        self._dists = tuple(self._dists)

    def __hash__(self):
        return hash(self._dists)

    @classmethod
    def _map_class(cls):
        return FrozenDistEnvMap


class DistEnvMapABC(_Mapping):

    __metaclass__ = _abc.ABCMeta

    def __init__(self, env):
        self._dict = {}
        self._env = env

    def __contains__(self, key):
        return key in self._dict

    def __getitem__(self, key):

        name = _dists_misc.normalized_dist_name(key)

        try:
            return self._dict[name]
        except KeyError:
            raise _exc.DistNotFound(key)

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    @property
    def env(self):
        return self._env


class DistEnvMap(DistEnvMapABC, _MutableMapping):

    def __delitem__(self, key):

        name = _dists_misc.normalized_dist_name(key)

        try:
            del self._dict[name]
        except KeyError:
            raise _exc.DistNotFound(key)

        for i, dist in enumerate(self.env._dists):
            if _dists_misc.normalized_dist_name(dist) == name:
                del self.enviroment._dists[i]

    def __setitem__(self, key, value):

        name = _dists_misc.normalized_dist_name(key)

        self._dict[name] = value
        self.env._dists.append(value)


class FrozenDistEnvMap(DistEnvMapABC):
    def __hash__(self):
        return hash(self._dict)
