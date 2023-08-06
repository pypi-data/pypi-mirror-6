import argparse
import os
import sys

from setuptools import setup, find_packages
from setuptools.command.develop import develop as develop_command
#from setuptools.command.install import install as install_command

try:
# catch importerror

    from pbr.packaging import parse_requirements
    from pbr.packaging import LocalInstall as install_command

    MINIMAL = ('Perform the minimal, "localhost discovery" only Satori '
            'installation. i.e exclude heavy dependencies: '
            'novaclient, paramiko, etc.')

    def add_option(cls, tag, description, boolean=False):
        """Return tuple of user_options, boolean_options."""
        cls.user_options = [
            (tag, None, description)
        ] + cls.user_options

        if boolean:
            cls.boolean_options = [tag] + cls.boolean_options

        # no dupes
        cls.user_options = list(set(cls.user_options))
        cls.boolean_options = list(set(cls.boolean_options))
        return cls.user_options, cls.boolean_options


    class CustomDevelopCommand(develop_command):

        command_name = 'develop'
        user_options, boolean_options = add_option(
            develop_command, 'minimal', MINIMAL, boolean=True)

        def __init__(self, *args, **kwargs):
            self.minimal = None
            develop_command.__init__(self, *args, **kwargs)

        def run(self, *args, **kwargs):
            print "MODIFIED RUN: %s" % self.__class__
            if self.minimal:
                self.distribution.install_requires = (
                    parse_requirements(
                        ['minimal-requirements.txt']))
                print "SELF.MINIMAL"
            print "install requires: %s" % (
                    self.distribution.install_requires)
            develop_command.run(self, *args, **kwargs)


    class CustomInstallCommand(install_command):

        command_name = 'install'
        user_options, boolean_options = add_option(
            install_command, 'minimal', MINIMAL, boolean=True)

        def __init__(self, *args, **kwargs):
            self.minimal = None
            install_command.__init__(self, *args, **kwargs)

        def run(self, *args, **kwargs):
            print "MODIFIED RUN: %s" % self.__class__
            if self.minimal:
                self.distribution.install_requires = (
                    parse_requirements(
                        ['minimal-requirements.txt']))
                print "SELF.MINIMAL"
            print "install requires: %s" % (
                    self.distribution.install_requires)
            install_command.run(self, *args, **kwargs)

except ImportError:
    pass

"""
def parse():
    if '--help' not in sys.argv:
        parser = argparse.ArgumentParser(description="Satori installation options.")
        parser.add_argument("--minimal", action="store_true", help=MINIMAL)
        config, unknown = parser.parse_known_args()
        if config.minimal:


    if '--minimal' in sys.argv:
            print "SETTING PBR_REQUIREMENTS_FILES"
            os.environ['PBR_REQUIREMENTS_FILES'] = 'minimal-requirements.txt'
            sys.argv.remove('--minimal')
"""

