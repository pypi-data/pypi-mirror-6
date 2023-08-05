import json
import glob
import os
import re

from exceptions import DuplicateJSONFile, InvalidClientInput


class ConfigurationPanda(object):

    def __init__(self, config_files_location_env_vars):
        """
        The constructor creates an attribute on the object for each
        JSON file found in each directory specified by
        config_files_location_env_vars.

        Args:
            config_files_location_env_vars (list): List of
                environment variables which point to directories containing
                configuration files.

        Raises:
            DuplicateJSONFile: When an attempt is
                made to load two JSON files with the same name.

        """
        if not isinstance(config_files_location_env_vars, list):
            raise InvalidClientInput(
                'config_files_location_env_vars must by a list.')

        configuration_files = (
            self._configuration_files(config_files_location_env_vars))

        for configuration_file in configuration_files:
            attribute_name = re.search(
                r"./([_A-Za-z0-9]+).json", configuration_file).groups()[0]

            self._check_for_existing_attribute(attribute_name)
            self._load_data_onto_attribute(attribute_name, configuration_file)

        self._load_environment_variables()

    def _configuration_files(self, config_files_location_env_vars):
        configuration_files = list()
        for env_var in config_files_location_env_vars:
            try:
                configuration_files.extend(glob.glob(
                    os.environ[env_var] + '/*.json'))
            except KeyError:
                raise InvalidClientInput('The environment variable specified '
                                         'by the client ({}) for use by '
                                         'the constructor does not exist'
                                         'on the system.'.format(env_var))
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
        if hasattr(self, 'environment_variables'):
            for env_var in self.environment_variables:
                os.environ[env_var] = self.environment_variables[env_var]

