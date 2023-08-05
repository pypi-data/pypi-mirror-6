"""Distribution packages miscellany."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"


def dist_repr(dist):
    attrnames = ['location', 'metadata', 'project_name', 'version',
                 'py_version', 'platform', 'precedence']
    attrs = []
    for name in attrnames:
        try:
            value = getattr(dist, name)
        except AttributeError:
            pass
        else:
            if value is not None:
                attrs.append((name, value))
    return '{}({})'.format(dist.__class__.__name__,
                           ', '.join('{}={!r}'.format(name, value)
                                     for name, value in attrs))


def normalized_dist_name(dist):
    try:
        name = dist.project_name
    except AttributeError:
        name = dist
    return name.lower()
