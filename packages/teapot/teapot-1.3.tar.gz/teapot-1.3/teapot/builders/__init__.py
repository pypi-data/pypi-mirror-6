"""
Contains all teapot builders logic.
"""

import os
import re
import json
import math
import signal
import hashlib
import subprocess

from contextlib import contextmanager
from threading import Thread
from datetime import datetime

from teapot.log import LOGGER, print_normal, print_error
from teapot.log import Highlight as hl
from teapot.filters import Filtered
from teapot.environments import make_environment, DEFAULT_ENVIRONMENT_NAME
from teapot.extensions import parse_extension


def make_builders(attendee, builders):
    """
    Make a list of builders from a dictionary.
    """

    if not builders:
        return []

    return [make_builder(attendee, name, attributes) for name, attributes in builders.items()]

def make_builder(attendee, name, attributes):
    """
    Make a builder from its attributes.
    """

    if not isinstance(attributes, dict):
        raise ValueError('builder attributes must be a dictionary.')

    tags = attributes.get('tags')

    if not tags:
        tags = []
    elif isinstance(tags, basestring):
        tags = [tags]

    commands = attributes.get('commands', [])

    if isinstance(commands, basestring):
        commands = [commands]

    clean_commands = attributes.get('clean_commands', [])

    if isinstance(clean_commands, basestring):
        clean_commands = [clean_commands]

    filters = attributes.get('filters')
    prefix = attributes.get('prefix')

    if prefix is True:
        prefix = name

    environment = attributes.get('environment', DEFAULT_ENVIRONMENT_NAME)

    if environment:
        if isinstance(environment, basestring):
            environment = attendee.party.environment_register.get_environment_by_name(environment)
        else:
            environment = make_environment(attendee.party.environment_register, None, environment)
    else:
        environment = make_environment(attendee.party.environment_register, None, {})

    return Builder(
        attendee=attendee,
        name=name,
        tags=tags,
        commands=commands,
        environment=environment,
        filters=filters,
        directory=attributes.get('directory'),
        prefix=prefix,
        clean_commands=clean_commands,
    )


class Builder(Filtered):

    """
    A Builder represents a way to build an attendee.
    """

    def __init__(self, attendee, name, tags, commands, environment, filters=[], directory=None, prefix=None, clean_commands=[]):
        """
        Initialize a builder attached to `attendee` with the specified `name`.

        A builder may have `tags`, which must be a list of strings.

        You must specify `commands`, a list of commands to call for the build to
        take place.

        `environment` is the environment to use for the build.

        `filters` is a list of filters that must all validate in order for the
        build to be active in the current environment.

        `directory`, if specified, is a directory relative to the source root,
        where to go before issuing the build commands.

        `prefix` is a prefix that will be added to the right of the global
        prefix inside the $PREFIX variable.

        `clean_commands` is a list of commands to run to clean the install.
        Those commands are executed in sequence until the last one, even if one
        of them fails.
        """

        if not commands:
            raise ValueError('A builder must have at least one command.')

        assert environment

        self.attendee = attendee
        self.name = name
        self.tags = tags
        self.commands = commands or []
        self.environment = environment
        self.directory = directory or None
        self.prefix = prefix or ''
        self.clean_commands = clean_commands

        Filtered.__init__(self, filters=filters)

    def __str__(self):
        """
        Get the name of the builder.
        """

        return self.name

    def __repr__(self):
        """
        Get a representation of the builder.
        """

        return '<%s.%s(name=%r, tags=%r, commands=%r)>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            self.name,
            self.tags,
            self.commands,
        )

    @contextmanager
    def chdir(self, path):
        """
        Change the current directory.
        """

        old_path = os.getcwd()

        LOGGER.debug('Moving to: %s', hl(path))
        os.chdir(path)

        try:
            yield path
        finally:
            LOGGER.debug('Moving back to: %s', hl(old_path))
            os.chdir(old_path)

    def build(self, build_directory, log_file=None, verbose=False):
        """
        Build the attendee.

        `build_directory` is the directory to build into.

        `log_file`, if specified, is a file object to write the output to.

        `verbose` is a flag that, if truthy, cause the build output to be
        printed on standard output as the build progresses.
        """

        if self.directory:
            source_tree_path = os.path.join(build_directory, self.directory)
        else:
            source_tree_path = build_directory

        if log_file:
            log_file.write('Build started in %s at %s.\n' % (source_tree_path, datetime.now().strftime('%c')))

        with self.chdir(source_tree_path):

            with self.environment.enable() as env:
                if env.shell:
                    LOGGER.info('Building within: %s', hl(' '.join(env.shell)))
                else:
                    LOGGER.info('Building within %s.', hl('the default system shell'))

                if log_file:
                    if env.shell:
                        log_file.write('Using "%s" as a shell.\n' % ' '.join(env.shell))
                    else:
                        log_file.write('Using system shell.\n')

                for key, value in os.environ.iteritems():
                    LOGGER.debug('%s: %s', key, hl(value))

                for index, command in enumerate(self.commands):
                    command = self.apply_extensions(command)
                    numbered_prefix = ('%%0%sd' % int(math.ceil(math.log10(len(self.commands))))) % index

                    LOGGER.important('%s: %s', numbered_prefix, hl(command))

                    if log_file:
                        log_file.write('%s: %s\n' % (numbered_prefix, command))

                    if env.shell:
                        process = subprocess.Popen(env.shell + [command], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    else:
                        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    def handler(signum, frame):
                        LOGGER.warning('The building process was interrupted by the user.')
                        process.terminate()

                    previous_handler = signal.signal(signal.SIGINT, handler)

                    mixed_output = []

                    try:
                        def read_stdout():
                            for line in iter(process.stdout.readline, ''):
                                mixed_output.append((print_normal, line))

                                if log_file:
                                    log_file.write(line)

                                if verbose:
                                    print_normal(line)

                        def read_stderr():
                            for line in iter(process.stderr.readline, ''):
                                mixed_output.append((print_error, line))

                                if log_file:
                                    log_file.write(line)

                                if verbose:
                                    print_error(line)

                        stdout_thread = Thread(target=read_stdout)
                        stdout_thread.daemon = True
                        stdout_thread.start()

                        stderr_thread = Thread(target=read_stderr)
                        stderr_thread.daemon = True
                        stderr_thread.start()

                        stdout_thread.join()
                        stderr_thread.join()

                        process.wait()

                    finally:
                        signal.signal(signal.SIGINT, previous_handler)

                    if log_file:
                        log_file.write('\n')

                    if process.returncode != 0:
                        if not verbose:
                            for func, line in mixed_output:
                                func(line)

                        if log_file:
                            log_file.write('Command failed with status: %s\n' % process.returncode)
                            log_file.write('Build failed at %s.\n' % datetime.now().strftime('%c'))

                        raise subprocess.CalledProcessError(returncode=process.returncode, cmd=command)

        if log_file:
            log_file.write('Build succeeded at %s.\n' % datetime.now().strftime('%c'))

    def clean(self):
        """
        Clean the attendee.
        """

        if not self.clean_commands:
            LOGGER.info('Cleaning builder %s: no clean commands specified. Doing nothing.', hl(self))

        else:
            LOGGER.info('Cleaning builder: %s', hl(self))

            with self.environment.enable() as env:
                if env.shell:
                    LOGGER.info('Executing clean commands within: %s', hl(' '.join(env.shell)))
                else:
                    LOGGER.info('Executing clean commands within %s.', hl('the default system shell'))

                for key, value in os.environ.iteritems():
                    LOGGER.debug('%s: %s', key, hl(value))

                for index, command in enumerate(self.clean_commands):
                    command = self.apply_extensions(command)
                    numbered_prefix = ('%%0%sd' % int(math.ceil(math.log10(len(self.commands))))) % index

                    LOGGER.important('%s: %s', numbered_prefix, hl(command))

                    if env.shell:
                        process = subprocess.Popen(env.shell + [command], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    else:
                        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    def handler(signum, frame):
                        LOGGER.warning('The cleaning process was interrupted by the user.')
                        process.terminate()

                    previous_handler = signal.signal(signal.SIGINT, handler)

                    try:
                        def read_stdout():
                            for line in iter(process.stdout.readline, ''):
                                LOGGER.debug(line.rstrip())

                        def read_stderr():
                            for line in iter(process.stderr.readline, ''):
                                LOGGER.debug(line.rstrip())

                        stdout_thread = Thread(target=read_stdout)
                        stdout_thread.daemon = True
                        stdout_thread.start()

                        stderr_thread = Thread(target=read_stderr)
                        stderr_thread.daemon = True
                        stderr_thread.start()

                        stdout_thread.join()
                        stderr_thread.join()

                        process.wait()

                    finally:
                        signal.signal(signal.SIGINT, previous_handler)

                    if process.returncode != 0:
                        LOGGER.warning('Command failed with status: %s', process.returncode)

            LOGGER.info('Clean succeeded at %s.', datetime.now().strftime('%c'))

    def apply_extensions(self, command):
        """
        Apply the extensions to the command.
        """

        def replace(match):
            code = match.group('code')

            return str(parse_extension(code, self))

        return re.sub(r'\{{(?P<code>[\w\s()]+)}}', replace, command)

    @property
    def signature(self):
        """
        Get the signature of the builder.
        """

        data = {
            'name': self.name,
            'tags': self.tags,
            'commands': self.commands,
            'environment': self.environment.signature,
            'directory': self.directory,
            'prefix': self.prefix,
        }

        algorithm = hashlib.sha1()
        algorithm.update(json.dumps(data))

        result = algorithm.hexdigest()

        LOGGER.debug('%s\'s signature is: %s', hl(self), hl(result))

        return result
