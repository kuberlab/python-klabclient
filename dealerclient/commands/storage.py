
import json

from cliff import show

from dealerclient.commands import base
from dealerclient import exceptions
from dealerclient import utils


def format_storage_list(storage=None):
    return format_storage(storage, lister=True)


def format_storage(storage=None, lister=False):
    columns = ('Type', 'Name',)
    data = (
        storage.Type,
        storage.Name,
    )

    if not lister:
        # All below needed for dynamic column rendering.
        # Sources may have any new attributes in the future so
        # we can't refer to static field list.
        attrs = utils.get_public_attr(
            storage,
            except_of=[
                'resource_name', 'defaults', 'manager', 'Type', 'Name'
            ]
        )
        for k, v in attrs.items():
            columns += (k,)
            if isinstance(v, (list, dict)):
                v = json.dumps(v, indent=4)

            data += (v,)

    return columns, data


class List(base.DealerLister):
    """List all available storage for cluster."""

    def _get_format_function(self):
        return format_storage_list

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)
        base.add_workspace_arg(parser)

        parser.add_argument(
            'cluster_id',
            help='Cluster ID.'
        )
        return parser

    @base.workspace_aware
    def _get_resources(self, args):
        dealer_client = self.app.client

        return dealer_client.storage.list(args.workspace, args.cluster_id)


class Get(show.ShowOne):
    """Show specific storage."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)
        base.add_workspace_arg(parser)

        parser.add_argument(
            'cluster_id',
            help='Cluster ID.'
        )
        parser.add_argument('name', help='Storage name.')

        return parser

    @base.workspace_aware
    def take_action(self, args):
        dealer_client = self.app.client
        storage = dealer_client.storage.list(args.workspace, args.cluster_id)

        for st in storage:
            if st.Name == args.name:
                return format_storage(st)

        raise exceptions.DealerClientException(
            'Storage "%s" not found in storage list.' % args.name
        )
