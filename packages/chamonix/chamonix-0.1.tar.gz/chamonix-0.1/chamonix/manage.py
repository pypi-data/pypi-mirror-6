# -*- coding: utf-8 -*-
import os
import argparse

from chamonix.config import settings


class CLI(object):
    """
    A command line interface for management utilities.
    """

    _CMD_CREATE_MSGS = 'cd %s\n\
                        mkdir -p i18n/en_US/LC_MESSAGES/\n\
                        pygettext -a -v -d messages -o i18n/messages.po \*.py templates/\*.html' % settings.ROOT

    _CMD_COMPILE_MSGS = 'cd %s\n\
                         msgfmt -o i18n/fr_FR/LC_MESSAGES/messages.mo i18n/fr_FR/LC_MESSAGES/messages.po' % settings.ROOT

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            'command',
            help="Command to execute"
        )
        self.args = self.parser.parse_args()

    def start(self):
        command = self.args.command
        try:
            func = getattr(self, command)
        except AttributeError, e:
            raise SystemExit('No such command `%s`' % command)
        func()

    def create_messages(self):
        """
        Create needed path and files for i18n
        """
        os.system(self._CMD_CREATE_MSGS)

    def compile_messages(self):
        """
        Compile i18n messages
        """
        os.system(self._CMD_COMPILE_MSGS)

    def db_init(self):
        pass

def main():
    cli = CLI()
    cli.start()

if __name__ == '__main__':
    main()
