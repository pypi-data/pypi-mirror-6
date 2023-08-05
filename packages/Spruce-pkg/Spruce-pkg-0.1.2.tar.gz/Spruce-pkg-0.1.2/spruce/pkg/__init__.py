"""Packaging.

Inspection and manipulation of projects and their distribution packages.

This is an extension of :mod:`setuptools` and :mod:`pkg_resources` from
:pypi:`setuptools`.

"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__credits__ = ["Ivan D Vasin"]
__maintainer__ = "Ivan D Vasin"
__email__ = "nisavid@gmail.com"
__docformat__ = "restructuredtext"

from ._exc import *
from ._envs import *
from ._dists import *
from ._dists_misc import *
from ._misc import *
from ._projects import *
from ._projects_misc import *
from ._requirements import *
from ._std import *
