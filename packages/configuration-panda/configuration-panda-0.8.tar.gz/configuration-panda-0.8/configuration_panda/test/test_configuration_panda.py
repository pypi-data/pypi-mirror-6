import os
from unittest import TestCase

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

    def setUp(self):
        self.configuration_panda = ConfigurationPanda(
            ['PRIMARY_CONFIGURATION_FILES', 'SECONDARY_CONFIGURATION_FILES'])

    def tearDown(self):
        #Remove all environment variables set during setUp().
        for variable in self.configuration_panda.environment_variables:
            del os.environ[variable]

    def test_constructor_with_invalid_environment_variables(self):
        """
        Prove __init__() throws InvalidParameter when given a bad env_var.

        """
        self.assertRaises(InvalidParameter,
                          ConfigurationPanda,
                          ['NON_EXISTENT_ENV_VAR'])

    def test_constructor_with_invalid_1st_parameter_type(self):
        """
        Prove __init__() throws InvalidParameter when given a non-list
        as its first parameter.

        """
        self.assertRaises(InvalidParameter,
                          ConfigurationPanda,
                          'NON_EXISTENT_ENV_VAR')

        self.assertRaises(InvalidParameter,
                          ConfigurationPanda,
                          123)

        self.assertRaises(InvalidParameter,
                          ConfigurationPanda,
                          {'key': 'value'})

    def test_constructor(self):
        """
        Prove that the constructor executed in the setUp() method
        correctly sets object attributes based on the ldap.json
        and smtp.json mock configuration files included in the
        primary_configuration_files  directory.

        """
        self.assertDictContainsSubset(
            {u'url': u'smtp.yourschool.edu',
             u'login': u'testaccount2',
             u'password': u'testaccount2password'},
            self.configuration_panda.smtp['TestAccount2'])

        self.assertDictContainsSubset(
            {u'url': u'ldaps://primaryldap.yourschool.edu:111',
             u'login': u'cn=LDAP Testing',
             u'password': u'LDAP Password'},
            self.configuration_panda.ldap['primary'])

        self.assertEquals(self.configuration_panda.smtp['TestAccount1']['url'],
                          'smtp.yourschool.edu')

        self.assertEquals(self.configuration_panda.ldap['primary']['url'],
                          'ldaps://primaryldap.yourschool.edu:111')

    def test_constructor_duplicate_configuration_filenames(self):
        """
        Prove that ConfigurationPanda.__init__() throws a
        DuplicateJSONFile when more an attempt is made to
        load data onto an existing object attribute (which would only happen
        if a filename being loaded has a name collision with an existing
        object attribute).

        """

        # Test for duplicate file names in distinct directories.
        self.assertRaises(
            DuplicateJSONFile,
            ConfigurationPanda,
            ['PRIMARY_CONFIGURATION_FILES', 'DUPLICATE_CONFIGURATION_FILES']
        )

        # Test for duplicate file names as a result of passing the
        # same environment variable into the constructor multiple times.
        self.assertRaises(
            DuplicateJSONFile,
            ConfigurationPanda,
            ['PRIMARY_CONFIGURATION_FILES', 'PRIMARY_CONFIGURATION_FILES']
        )

    def test_constructor_with_overriding_env_var(self):
        """
        Prove that ConfigurationPanda.__init__() throws an
        ExistingEnvironmentVariable exception when an attempt is made
        to set the value of an existing environment variable.

        """

        self.assertRaises(ExistingEnvironmentVariable,
                          ConfigurationPanda,
                          ['PRIMARY_CONFIGURATION_FILES'])

    def test_constructor_for_environment_variable_assignment(self):
        """
        Prove that ConfigurationPanda.__init__() sets environment variables
        from the contents of a file called 'environment_variables.json'
        when it located during the JSON file search.

        """

        self.assertEqual(os.environ['MY_FAVORITE_FOOD'], "Dumplings")
        self.assertEqual(os.environ['MY_WORST_NIGHTMARE'], "The Noodle Dream")