import os
from unittest import TestCase
import pytest

from ..configuration_panda import ConfigurationPanda
from ..exceptions import (
    DuplicateJSONFile, InvalidParameter, ExistingEnvironmentVariable)


class Test_ConfigurationPanda(TestCase):
    """
    Exercises the functionality of the ConfigurationPanda class.

    """

    @classmethod
    def setUpClass(cls):
        test_file_path = os.path.dirname(__file__)

        os.environ['PRIMARY_CONFIGURATION_FILES'] = \
            test_file_path + '/primary_configuration_files'
        os.environ['SECONDARY_CONFIGURATION_FILES'] = \
            test_file_path + '/secondary_configuration_files'
        os.environ['DUPLICATE_CONFIGURATION_FILES'] = \
            test_file_path + '/duplicate_configuration_files'

    def test_constructor_with_invalid_environment_variables(self):
        """
        Prove __init__() throws InvalidParameter when given a
        non-existent env_var.

        """
        with pytest.raises(InvalidParameter):
            ConfigurationPanda(['NON_EXISTENT_ENV_VAR'])

    def test_constructor_attribute_existence(self):
        """
        Prove that the constructor correctly sets object attributes
        based on the ldap.json and environment_variables.json mock
        configuration files included in the
        'primary_configuration_files' directory.

        """
        with ConfigurationPanda(['PRIMARY_CONFIGURATION_FILES']) as test_object:
            assert hasattr(test_object, 'ldap')
            assert hasattr(test_object, 'environment_variables')

    def test_constructor_attribute_access_via_dictionary_syntax(self):
        """
        Prove that ConfigurationPanda object attributes can be
        accessed using dictionary style syntax.

        """
        with ConfigurationPanda(['PRIMARY_CONFIGURATION_FILES']) as test_object:
            assert test_object['ldap']
            assert test_object['environment_variables']

    def test_constructor_attribute_content_is_correct(self):
        """
        Prove that after construction, a ConfigurationPanda object's
        attributes have the correct content from the JSON files.

        """

        with ConfigurationPanda(
                ['SECONDARY_CONFIGURATION_FILES']) as test_object:
            assert test_object.smtp['TestAccount1'] == dict(
                url='smtp.yourschool.edu',
                login='testaccount1',
                password='testaccount1password'
            )
            assert test_object.smtp['TestAccount1'] == dict(
                url='smtp.yourschool.edu',
                login='testaccount1',
                password='testaccount1password')

    def test_constructor_duplicate_configuration_filenames(self):
        """
        Prove that ConfigurationPanda.__init__() throws
        DuplicateJSONFile when an attempt is made to load data onto
        an existing object attribute.

        """
        with pytest.raises(DuplicateJSONFile):
            ConfigurationPanda(['PRIMARY_CONFIGURATION_FILES',
                                'PRIMARY_CONFIGURATION_FILES'])

    def test_constructor_with_overriding_env_var(self):
        """
        Prove that ConfigurationPanda.__init__() throws an
        ExistingEnvironmentVariable exception when an attempt is made
        to set the value of an existing environment variable.

        """
        with ConfigurationPanda(['PRIMARY_CONFIGURATION_FILES']) as test_object:
            with pytest.raises(ExistingEnvironmentVariable):
                ConfigurationPanda(['PRIMARY_CONFIGURATION_FILES'])

    def test_constructor_for_environment_variable_assignment(self):
        """
        Prove that ConfigurationPanda.__init__() sets environment variables
        from the contents of a file called 'environment_variables.json'
        when it located during the JSON file search.

        """

        with ConfigurationPanda(['PRIMARY_CONFIGURATION_FILES']) as test_object:
            self.assertEqual(os.environ['MY_FAVORITE_FOOD'], "Dumplings")
            self.assertEqual(
                os.environ['MY_WORST_NIGHTMARE'], "The Noodle Dream")