"""
**ConfigurationPanda provides easy loading and access to the data elements of
JSON based configuration files.**

It works by finding JSON configuration files within locations specified
by environment variables loads the contents of each file onto an object
attribute so that program internals can easily obtain necessary settings
without developers having to write routine open() and json parsing operations.

It is an opinionated library which attempts to encourage fellow developers to:

1.  Avoid Borg-like single configuration files containing all your
    passwords, settings, etc.  Instead, as each configuration file
    becomes a namespace on the ConfigurationPanda object, the contents of
    that file should be explicitly tied to the namespace.

2.  Avoid hardcoding configuration file paths into your programs.
    The program stubbornly insists on working with environment variables
    only.

3.  Use JSON rather than CONF files, which are much more portable when
    operating in a heterogeneous programming environment.  My condolences
    if you have to work with .Net

Usage
-----

Assuming that an environment variable 'SHARED_CONFIG_FILES' exists
and points to a directory containing multiple JSON files, including
the following::

    ldap.json
      {
        "primary": {
            "url": "ldaps://primaryldap.example.edu:111",
            "login": "cn=LDAP Testing",
            "password": "LDAP Password"
        }
      }

    smtp.json
      {
        "TestAccount1": {
            "url": "smtp.yourschool.edu",
            "login": "testaccount1",
            "password": "testaccount1password"
        }
      }

You would access the contents of those configuration files like this::

    >>> from configuration_panda import ConfigurationPanda
    >>> program_settings = ConfigurationPanda(['SHARED_CONFIG_FILES'])
    >>> program_settings.ldap['primary']['url']
    ldaps://primaryldap.example.edu:111
    >>> program_settings.smtp['TestAccount1']['login']
    testaccount1

Or, if you prefer dictionary-style syntax::

    >>> from configuration_panda import ConfigurationPanda
    >>> program_settings = ConfigurationPanda(['SHARED_CONFIG_FILES'])
    >>> program_settings['ldap']['primary']['url']
    ldaps://primaryldap.example.edu:111
    >>> program_settings['smtp']['TestAccount1']['login']
    testaccount1

BONUS! Set Environment Variables
--------------------------------
ConfigurationPanda can also set additional environment variables for you!

If a JSON file named 'environment_variables.json' is found during
directory scanning, an attempt will be made to create an environment variable
from each entry within the JSON file.

For instance::

    environment_variables.json
      {
        "MY_FAVORITE_FOOD": "Dumplings",
        "MY_WORST_NIGHTMARE": "The Noodle Dream"
      }

This functionality allows you to dynamically insert environment variables
at runtime rather than having to make them a permanent fixture in a
.bash_profile or .bash_rc file.


"""

from configuration_panda import ConfigurationPanda

__version__ = '0.6'
