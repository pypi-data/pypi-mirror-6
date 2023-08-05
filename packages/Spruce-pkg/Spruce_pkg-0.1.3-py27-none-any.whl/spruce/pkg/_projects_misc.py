"""Projects miscellany."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"


def normalized_project_name(project):
    try:
        name = project.name
    except AttributeError:
        name = project
    return name.lower()
