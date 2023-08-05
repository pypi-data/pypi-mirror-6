import os
from unittest import TestCase

from ..configuration_panda import ConfigurationPanda
from ..exceptions import DuplicateJSONFile, InvalidClientInput


class Test_ConfigurationPanda(TestCase):
    """
    Exercises the functionality of the ConfigurationPanda class.

    """

    def setUp(self):
        self.test_file_path = os.path.dirname(__file__)

        os.environ['PRIMARY_CONFIGURATION_FILES'] = \
            self.test_file_path + '/primary_configuration_files'
        os.environ['SECONDARY_CONFIGURATION_FILES'] = \
            self.test_file_path + '/secondary_configuration_files'

        self.configuration_panda = ConfigurationPanda(
            ['PRIMARY_CONFIGURATION_FILES', 'SECONDARY_CONFIGURATION_FILES'])

    def test_constructor_with_invalid_environment_variables(self):
        """
        Prove __init__() throws InvalidClientInput when given a bad env_var.

        """
        self.assertRaises(InvalidClientInput,
                          ConfigurationPanda,
                          ['NON_EXISTENT_ENV_VAR'])

    def test_constructor_with_invalid_1st_parameter_type(self):
        """
        Prove __init__() throws InvalidClientInput when given a non-list
        as its first parameter.

        """
        self.assertRaises(InvalidClientInput,
                          ConfigurationPanda,
                          'NON_EXISTENT_ENV_VAR')

        self.assertRaises(InvalidClientInput,
                          ConfigurationPanda,
                          123)

        self.assertRaises(InvalidClientInput,
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

        os.environ['DUPLICATE_CONFIGURATION_FILES'] = \
            self.test_file_path + '/duplicate_configuration_files'

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