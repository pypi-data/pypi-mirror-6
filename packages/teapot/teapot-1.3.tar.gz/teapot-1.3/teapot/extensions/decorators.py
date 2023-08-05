"""
The extensions decorators.
"""

import re
import itertools

from functools import wraps


EXTENSIONS = {}

class NoSuchExtensionError(ValueError):

    """
    No extension exists with the specified name.
    """

    def __init__(self, name):
        """
        Create an NoSuchExtensionError for the specified extension `name`.
        """

        self.name = name

        super(NoSuchExtensionError, self).__init__(
            'No extension with the specified name: %s' % name
            )


class DuplicateExtensionError(ValueError):

    """
    Another extension with the same name exists.
    """

    def __init__(self, name):
        """
        Create a DuplicateExtensionError for the specified extension `name`.
        """

        self.name = name

        super(DuplicateExtensionError, self).__init__(
            'Another extension was already registered with the name %r' % name
            )

class ExtensionParsingError(ValueError):

    """
    No valid extension could be parsed.
    """

    def __init__(self, code):
        """
        Create an ExtensionParsingError for the specified `code`.
        """

        self.code = code

        super(ExtensionParsingError, self).__init__(
            'No extension could be parsed from %r' % code,
        )


class ExtensionRecursionDetected(ValueError):

    """
    A recursion was detected in the extension callstack.
    """

    def __init__(self, callstack):
        """
        Create an ExtensionRecursionDetected for the specified `callstack`.
        """

        self.callstack = callstack

        callstack_output = '\n'.join(
            '%s(%s)' % (
                stack[0],
                ', '.join(map(repr, stack[1:])),
            )
            for stack
            in self.callstack
        )

        super(ExtensionRecursionDetected, self).__init__(
            'Extension recursion detected. Callstack was:\n' + callstack_output,
        )


class named_extension(object):

    """
    Registers a function to be a extension.
    """

    CALLSTACK = []

    def __init__(self, name, override=False, infinite_recursion_allowed=False):
        """
        Registers the function with the specified name.

        If another function was registered with the same name, a
        `DuplicateExtensionError` will be raised, unless `override` is truthy.
        """

        if name in EXTENSIONS and not override:
            raise DuplicateExtensionError(name)

        self.name = name
        self.infinite_recursion_allowed = infinite_recursion_allowed

    def __call__(self, func):
        """
        Registers the function and returns it unchanged.
        """

        @wraps(func)
        def decorated(*args):

            call_signature = tuple(itertools.chain([self.name], args))

            if not self.infinite_recursion_allowed and call_signature in self.CALLSTACK:
                raise ExtensionRecursionDetected(self.CALLSTACK + [call_signature])

            self.CALLSTACK.append(call_signature)

            try:
                return func(*args)

            finally:
                self.CALLSTACK.pop()

        EXTENSIONS[self.name] = decorated

        return decorated

def get_extension_by_name(name):
    """
    Get a extension by name.

    If no extension matches the specified name, an NoSuchExtensionError is raised.
    """

    if not name in EXTENSIONS:
        raise NoSuchExtensionError(name=name)

    return EXTENSIONS[name]

def parse_extension(code, builder):
    """
    Parse an extension call in `code` and calls it.

    `builder` will be passed to the extension call as the `builder` argument.

    The function returns the result of the extension call.
    """

    match = re.match(r'^(?P<name>[a-zA-Z_]+)(\((?P<args>(|(\s*\w+\s*)(,\s*\w+\s*)*))\)|)$', code)

    if not match:
        raise ExtensionParsingError(code=code)

    name = match.group('name')
    args = match.group('args')

    if args:
        args = [arg.strip() for arg in args.split(',')]
    else:
        args = []

    extension = get_extension_by_name(name)

    return extension(builder, *args)
