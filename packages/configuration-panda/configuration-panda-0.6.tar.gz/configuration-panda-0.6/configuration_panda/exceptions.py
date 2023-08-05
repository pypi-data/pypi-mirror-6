"""
Custom exceptions for ConfigurationPanda.

"""

class ConfigurationPandaError(Exception):
    """
    Base exception class for ConfigurationPanda Errors.
    """
    pass


class DuplicateJSONFile(ConfigurationPandaError):
    """
    Error to raise when an attempt is made to load a configuration file
    with the same names as a previously loaded file.

    """
    pass

class InvalidClientInput(ConfigurationPandaError):
    """
    Error to raise when an error arises from the use of invalid
    input provided by the client.

    """
