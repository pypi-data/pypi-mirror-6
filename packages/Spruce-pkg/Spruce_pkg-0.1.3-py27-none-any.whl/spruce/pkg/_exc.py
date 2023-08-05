"""Exceptions."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"


class Error(RuntimeError):
    pass


class NoDefinitiveProjectLocation(Error):

    def __init__(self, project, message=None, *args):
        self._project = project
        self._message = message
        super(NoDefinitiveProjectLocation, self).__init__(project, message,
                                                          *args)

    def __str__(self):
        message = 'no definitive location for project {!r}'\
                   .format(self.project)
        if self.message:
            message += ': ' + self.message
        return message

    @property
    def message(self):
        return self._message

    @property
    def project(self):
        return self._project


class DistNotFound(Error):

    def __init__(self, name=None, location=None, message=None, *args):
        self._location = location
        self._message = message
        self._name = name
        super(DistNotFound, self).__init__(name, location, message, *args)

    def __str__(self):
        message = 'no distribution package found'
        if self.name:
            message += ' with name {!r}'.format(self.name)
        if self.location:
            message += ' at {!r}'.format(self.location)
        if self.message:
            message += ': ' + self.message
        return message

    @property
    def location(self):
        return self._location

    @property
    def message(self):
        return self._message

    @property
    def name(self):
        return self._name


class IncompatibleRequirements(Error):

    def __init__(self, requirements, message=None, *args):
        self._requirements = requirements
        self._message = message
        super(IncompatibleRequirements, self).__init__(requirements, message,
                                                       *args)

    def __str__(self):
        message = 'incompatible requirements {}'\
                   .format(tuple(self.requirements))
        if self.message:
            message += ': ' + self.message
        return message

    @property
    def message(self):
        return self._message

    @property
    def requirements(self):
        return self._requirements


class IncompatibleRequirementsSpecs(Error):

    def __init__(self, requirements, specs, *args):

        specs = tuple(specs)

        self._requirement = requirements
        self._specs = specs

        message = 'incompatible specs {}'.format(specs)
        super(InconsistentRequirementSpecs, self)\
         .__init__(requirements, message, specs, *args)


class InvalidRequirement(Error):

    def __init__(self, requirement, message=None, *args):
        self._requirement = requirement
        self._message = message
        super(InvalidRequirement, self).__init__(requirement, message, *args)

    def __str__(self):
        message = 'invalid requirement {!r}'.format(str(self.requirement))
        if self.message:
            message += ': ' + self.message
        return message

    @property
    def message(self):
        return self._message

    @property
    def requirement(self):
        return self._requirement


class InconsistentRequirementSpecs(InvalidRequirement):

    def __init__(self, requirement, specs, *args):

        specs = tuple(specs)

        self._requirement = requirement
        self._specs = specs

        message = 'inconsistent specs {}'.format(specs)
        super(InconsistentRequirementSpecs, self)\
         .__init__(requirement, message, specs, *args)

    @property
    def specs(self):
        return self._specs

    @property
    def requirement(self):
        return self._requirement


class ProjectsNotFound(Error):

    def __init__(self, names=None, searchpaths=None, message=None, *args):
        self._message = message
        self._names = names
        self._searchpaths = searchpaths
        super(ProjectsNotFound, self).__init__(names, searchpaths, message,
                                               *args)

    def __str__(self):
        message = 'no projects found'
        if self.names:
            message += ' with names {!r}'.format(self.names)
        if self.searchpaths:
            message += ' at {!r}'.format(self.searchpaths)
        if self.message:
            message += ': ' + self.message
        return message

    @property
    def message(self):
        return self._message

    @property
    def names(self):
        return self._names

    @property
    def searchpaths(self):
        return self._searchpaths


class UpdateDistMetadataError(Error):

    def __init__(self, dist, cmd, message=None, *args):
        self._cmd = cmd
        self._dist = dist
        self._message = message
        super(UpdateDistMetadataError, self).__init__(dist, message, *args)

    def __str__(self):
        message = \
            'failed to update packaging metadata for distribution package {}'\
             ' using command {!r}'\
             .format(self.dist, self.cmd)
        if self.message:
            message += ': ' + self.message
        return message

    @property
    def cmd(self):
        return self._cmd

    @property
    def dist(self):
        return self._dist

    @property
    def message(self):
        return self._message


class UpdateMetadataError(Error):

    def __init__(self, location, cmd, message=None, *args):
        self._cmd = cmd
        self._location = location
        self._message = message
        super(UpdateMetadataError, self).__init__(location, message, *args)

    def __str__(self):
        message = \
            'failed to update packaging metadata at {!r} using command {!r}'\
             .format(self.location, self.cmd)
        if self.message:
            message += ': ' + self.message
        return message

    @property
    def cmd(self):
        return self._cmd

    @property
    def message(self):
        return self._message

    @property
    def location(self):
        return self._location
