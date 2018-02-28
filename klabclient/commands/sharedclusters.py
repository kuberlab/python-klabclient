import json

from cliff import command
from cliff import show

from klabclient.commands import base
from klabclient import utils


def format_list(cluster=None):
    return format(cluster, lister=True)


def format(cluster=None, lister=False):
    # "ID": "221",
    # "DisplayName": "testshare",
    # "From": {
    #             "WorkspaceName": "kuberlab-demo",
    #             "ProjectName": "demotest",
    #             "ClusterName": "minikube"
    #         },
    # "Active": true,
    # "WorkspaceName": "kuberlab-demo"
    if hasattr(cluster, 'WorkspaceName'):
        columns = ('ID', 'Display name', 'WorkspaceName',)
        data = (cluster.ID, cluster.DisplayName, cluster.WorkspaceName,)
    else:
        columns = ('ID', 'Display name', 'Global',)
        data = (cluster.ID, cluster.DisplayName, cluster.Global,)

    if cluster:
        if hasattr(cluster, 'Active'):
            columns += ('Active',)
            data += (cluster.Active,)

        if not lister:
            columns += ('From', 'Shared',)
            data = data + (
                json.dumps(cluster.From, indent=4),
                json.dumps(getattr(cluster, 'Shared', None), indent=4)
            )
            if hasattr(cluster, 'Links'):
                columns += ('Links',)
                data += (json.dumps(cluster.Links, indent=4),)
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class ListAvailable(base.KuberlabLister):
    """List all available shared clusters."""

    def _get_format_function(self):
        return format_list

    def _get_resources(self, args):
        klab_client = self.app.client

        return klab_client.sharedclusters.list_available()


class ListOwn(base.KuberlabLister):
    """List all own shared clusters."""

    def _get_format_function(self):
        return format_list

    def get_parser(self, prog_name):
        parser = super(ListOwn, self).get_parser(prog_name)

        return parser

    def _get_resources(self, args):
        klab_client = self.app.client

        return klab_client.sharedclusters.list_own()


class GetAvailable(show.ShowOne):
    """Show specific shared cluster."""

    def get_parser(self, prog_name):
        parser = super(GetAvailable, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument('id', help='Cluster id.')

        return parser

    @base.workspace_aware
    def take_action(self, args):
        klab_client = self.app.client
        project = klab_client.sharedclusters.get_available(
            args.workspace, args.id
        )

        return format(project)


class GetOwn(show.ShowOne):
    """Show specific shared cluster."""

    def get_parser(self, prog_name):
        parser = super(GetOwn, self).get_parser(prog_name)
        parser.add_argument('id', help='Cluster id.')

        return parser

    def take_action(self, args):
        klab_client = self.app.client
        project = klab_client.sharedclusters.get_own(args.id)

        return format(project)


class DeleteAvailable(command.Command):
    """Delete project."""

    def get_parser(self, prog_name):
        parser = super(DeleteAvailable, self).get_parser(prog_name)

        base.add_workspace_arg(parser)

        parser.add_argument(
            'id',
            nargs='+',
            help='Shared cluster ID(s).'
        )

        return parser

    @base.workspace_aware
    def take_action(self, args):
        klab_client = self.app.client

        utils.do_action_on_many(
            lambda s: klab_client.sharedclusters.delete_available(
                args.workspace, s
            ),
            args.id,
            "Request to delete shared cluster %s has been accepted.",
            "Unable to delete the specified shared cluster(s)."
        )


class DeleteOwn(command.Command):
    """Delete project."""

    def get_parser(self, prog_name):
        parser = super(DeleteOwn, self).get_parser(prog_name)

        parser.add_argument(
            'id',
            nargs='+',
            help='Shared cluster ID(s).'
        )

        return parser

    def take_action(self, args):
        klab_client = self.app.client

        utils.do_action_on_many(
            lambda s: klab_client.sharedclusters.delete_own(s),
            args.id,
            "Request to delete shared cluster %s has been accepted.",
            "Unable to delete the specified shared cluster(s)."
        )
