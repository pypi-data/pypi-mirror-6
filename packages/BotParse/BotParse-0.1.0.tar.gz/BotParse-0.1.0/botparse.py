#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013, Cameron White
import argparse
from StringIO import StringIO

parser_output = StringIO()

class BotParse:
    def __init__(self, description=None, epilog=None, add_help=True):
        self.parser = MainParser(
            add_help = False,
            description = description,
            epilog = epilog,
        )
        self.commands = self.parser.add_subparsers(
            dest='command',
            parser_class=CommandParser,
        )
        if add_help:
            self.commands.add_parser('!help')
    def add_command(self, *args, **kwargs):
        if 'add_help' not in kwargs or kwargs['add_help']:
            add_help = True
        kwargs['add_help'] = False
        command = self.commands.add_parser(*args, **kwargs)
        if add_help:
            command.add_argument(
                '--help', '-h',
                default = False, const=True, 
                action='store_const',
            )
        return command
    def format_help(self):
        return self.parser.format_help()
    def parse_args(self, namespace):
        return self.parser.parse_args(namespace)

class ArgumentParser(argparse.ArgumentParser):
    def _print_message(self, message, file=None):
        argparse.ArgumentParser._print_message(self, message, parser_output)
    def exit(self, status=0, message=None):
        if message:
            self._print_message(message, None)

class MainParser(ArgumentParser):
    def format_help(self):
        formatter = self._get_formatter()

        # description
        formatter.add_text(self.description)
        
        formatter.start_section('Commands')
        formatter.add_text(self._positionals.description)
        formatter.add_arguments(self._positionals._group_actions)
        formatter.end_section()
        
        # epilog
        formatter.add_text(self.epilog)

        # determine help from format above
        return formatter.format_help().strip()

class CommandParser(ArgumentParser):
    def format_help(self):
        return argparse.ArgumentParser.format_help(self).strip()
