#!/usr/bin/env python

from flask import current_app, Flask, request
from subprocess import Popen
import argparse
import logging
import sys

_logger = logging.getLogger('remosh')

def create_app(commands_file, log_file=None):
    """ Create the WSGI app and load configuration from file.

    Logging to log_file and sysout.
    """
    app = Flask('remosh')
    _init_logging(log_file)
    commands = {}
    with open(commands_file) as fh:
        for line in fh:
            command_id, command = [s.strip() for s in line.split(': ', 1)]
            commands[command_id] = command
            _logger.info('Intialized command: %s -> %s', command_id, command)
    app.config['commands'] = commands

    app.add_url_rule('/', 'exec_commnad', exec_commnad, methods=['POST'])

    return app


def exec_commnad():
    """ Handle incoming requests. """
    command_id = request.args.get('id')
    _logger.debug('Got request with id %s', command_id)
    command = current_app.config['commands'].get(command_id)
    if command:
        _logger.info('Executing command: %s', command)
        Popen(command, shell=True)
        return 'Goodie, goodie, will do!'
    else:
        _logger.info('Command not found with id: %s', command_id)
        return 'Err, unknown id.', 400


def _init_logging(log_file=None):
    """ Configure loggers. """
    sysout_handler = logging.StreamHandler(sys.stdout)
    _logger.addHandler(sysout_handler)
    if log_file:
        logfile_handler = logging.FileHandler(log_file)
        _logger.addHandler(logfile_handler)
    _logger.setLevel(logging.INFO)


def main():
    parser = argparse.ArgumentParser(prog='remosh')
    parser.add_argument('commands_file', help='Configuration file to use')
    parser.add_argument('-l', '--log-file', help='File to log to')
    args = parser.parse_args()
    app = create_app(args.config_file, args.log_file)
    app.run(port=8787)

if __name__ == '__main__':
    main()
