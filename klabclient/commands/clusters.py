
import json

from cliff import show

from klabclient.commands import base
from klabclient import utils


def format_cluster_list(cluster=None):
    return format_cluster(cluster, lister=True)


def format_cluster(cluster=None, lister=False):
    columns = ('ClusterID', 'ClusterType', 'Name',)
    data = (
        cluster.ClusterID,
        cluster.ClusterType,
        cluster.Name,
    )

    if not lister:
        # All below needed for dynamic column rendering.
        # Sources may have any new attributes in the future so
        # we can't refer to static field list.
        attrs = utils.get_public_attr(
            cluster,
            except_of=[
                'resource_name', 'defaults', 'manager', 'ClusterID',
                'ClusterType', 'Name', 'Active', 'WorkspaceName'
            ]
        )
        for k, v in attrs.items():
            columns += (k,)
            if isinstance(v, (list, dict)):
                v = json.dumps(v, indent=4)

            data += (v,)

    return columns, data


class List(base.KuberlabLister):
    """List all available clusters."""

    def _get_format_function(self):
        return format_cluster_list

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)
        base.add_workspace_arg(parser)

        return parser

    @base.workspace_aware
    def _get_resources(self, args):
        klab_client = self.app.client

        return klab_client.clusters.list(args.workspace)


class Get(show.ShowOne):
    """Show specific cluster."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)
        base.add_workspace_arg(parser)

        parser.add_argument('id', help='Cluster ID.')

        return parser

    @base.workspace_aware
    def take_action(self, args):
        klab_client = self.app.client
        cluster = klab_client.clusters.get(args.workspace, args.id)

        return format_cluster(cluster)
