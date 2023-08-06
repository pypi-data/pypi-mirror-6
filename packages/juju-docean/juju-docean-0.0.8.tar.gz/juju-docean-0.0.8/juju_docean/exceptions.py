
class ConfigError(ValueError):
    """ Environments.yaml configuration error.
    """


class PrecheckError(ValueError):
    """ A precondition check failed.
    """


class MissingKey(ValueError):
    """ User is missing ssh keys in digital ocean.
    """


class ConstraintError(ValueError):
    """ Specificed constraint is invalid.
    """


class TimeoutError(ValueError):
    """ Instance could not be provisioned before timeout.
    """
