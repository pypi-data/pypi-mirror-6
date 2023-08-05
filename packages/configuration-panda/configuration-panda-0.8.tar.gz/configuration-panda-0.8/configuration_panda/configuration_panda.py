import json
import glob
import os
import re

from exceptions import (
    DuplicateJSONFile, InvalidParameter, ExistingEnvironmentVariable)


class ConfigurationPanda(object):
    """
    Provides access to the contents of JSON configuration files using
    object or dictionary style syntax.

    """

    def __init__(self, config_files_location_env_vars=['CONFIGURATION_PANDA']):
        """
        The constructor creates an attribute on the object for each
        JSON file found in each directory specified by
        config_files_location_env_vars.

        Args:
            config_files_location_env_vars (list): List of
                environment variables which point to directories containing
                configuration files.  Defaults to a list containing
                the single entry 'CONFIGURATION_PANDA'.

        """
        if not isinstance(config_files_location_env_vars, list):
            raise InvalidParameter(
                'config_files_location_env_vars must by a list.')

        configuration_files = (
            self._configuration_files(config_files_location_env_vars))

        for configuration_file in configuration_files:
            attribute_name = re.search(
                r"./([_A-Za-z0-9]+).json", configuration_file).groups()[0]

            self._check_for_existing_attribute(attribute_name)
            self._load_data_onto_attribute(attribute_name, configuration_file)

        if hasattr(self, 'environment_variables'):
            self._load_environment_variables()

    def __getitem__(self, item):
        """
        Return instance attribute via dictionary syntax.

        """
        return self.__dict__[item]

    def _configuration_files(self, config_files_locations):
        """
        Raises:
            DuplicateJSONFile: When an attempt is
                made to load two JSON files with the same name.

        """
        configuration_files = list()
        for config_files_location in config_files_locations:
            try:
                configuration_files.extend(glob.glob(
                    os.environ[config_files_location] + '/*.json'))
            except KeyError:
                raise InvalidParameter('The environment variable specified '
                                       'by the client ({}) for use by '
                                       'the constructor does not exist '
                                       'on the system.'.format(
                                           config_files_location))
        return configuration_files

    def _check_for_existing_attribute(self, attribute_name):
        if hasattr(self, attribute_name):
            raise DuplicateJSONFile(
                "Two configuration files share the following name "
                "{}.  This is not allowed.".format(attribute_name))

    def _load_data_onto_attribute(self, attribute_name, configuration_file):
        with open(configuration_file) as configuration_file:
            try:
                self.__setattr__(
                    attribute_name, json.load(configuration_file))
            except ValueError:
                raise ValueError(
                    "The configuration file, {}, contains JSON "
                    "syntax errors.".format(configuration_file))

    def _load_environment_variables(self):
        """
        Set each element of self.environment_variables as an
        environment variable.

        Raises:
            ExistingEnvironmentVariable: If setting a environment variable
              would overwrite an existing value.

        """
        for env_var in self.environment_variables:
            if env_var in os.environ:
                raise ExistingEnvironmentVariable(
                    'An attempt was made to set the environment variable '
                    '{}, but this variable already exists.'.format(env_var)
                )
            os.environ[env_var] = self.environment_variables[env_var]
