
import abc
import os
import textwrap

from cliff import lister
import six

from klabclient import exceptions


DEFAULT_LIMIT = 100


@six.add_metaclass(abc.ABCMeta)
class KuberlabLister(lister.Lister):
    @abc.abstractmethod
    def _get_format_function(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _get_resources(self, args):
        """Gets a list of API resources (e.g. using client)."""
        raise NotImplementedError

    def _validate_parsed_args(self, parsed_args):
        # No-op by default.
        pass

    def take_action(self, args):
        self._validate_parsed_args(args)

        f = self._get_format_function()

        ret = self._get_resources(args)
        if not isinstance(ret, list):
            ret = [ret]

        data = [f(r)[1] for r in ret]

        if data:
            return f(ret[0])[0], data
        else:
            return f()


def cut(string, length=25):
    if string and len(string) > length:
        return "%s..." % string[:length]
    else:
        return string


def wrap(string, width=25):
    if string and len(string) > width:
        return textwrap.fill(string, width)
    else:
        return string


def add_workspace_arg(parser):
    parser.add_argument(
        '--workspace',
        default=os.environ.get('DEALER_WORKSPACE'),
        metavar='<workspace>',
        help='Workspace name.'
    )


def workspace_aware(func):
    def decorator(self, args):
        if hasattr(args, 'workspace'):
            if not args.workspace:
                raise exceptions.IllegalArgumentException(
                    "Provide workspace name via either --workspace "
                    "parameter or DEALER_WORKSPACE env variable."
                )
        return func(self, args)
    return decorator


def get_filters(parsed_args):
    filters = {}

    if parsed_args.filters:
        for f in parsed_args.filters:
            arr = f.split('=')

            if len(arr) != 2:
                raise ValueError('Invalid filter: %s' % f)

            filters[arr[0]] = arr[1]

    return filters
