import yaml

from cliff import command
from cliff import show

from dealerclient.commands import base
from dealerclient import utils


def format_list(mlapp=None):
    return format(mlapp, lister=True)


def format(mlapp=None, lister=False):
    # "ClusterName": "string",
    # "Description": "string",
    # "DisableReason": "string",
    # "DisplayName": "string",
    # "Enabled": true,
    # "Environment": "string",
    # "GlobalClusterID": "string",
    # "GlobalClusterName": "string",
    # "Name": "string",
    # "ProjectDisplayName": "string",
    # "ProjectName": "string",
    # "RepositoryCreateName": "string",
    # "RepositoryCreateOwner": "string",
    # "RepositoryCreateService": "string",
    # "RepositoryDir": "string",
    # "RepositoryID": "string",
    # "RepositoryPrivate": true,
    # "RepositoryURL": "string",
    # "SharedClusterID": "string",
    # "SharedClusterName": "string",
    # "WorkspaceDisplayName": "string",
    # "WorkspaceName": "string"
    columns = (
        'Name',
        'Display name',
        'Enabled',
        'Cluster',
        'Workspace',
        'Project',
    )

    if mlapp:
        data = (
            mlapp.Name,
            mlapp.DisplayName,
            mlapp.Enabled,
            mlapp.ClusterName,
            mlapp.WorkspaceName,
            mlapp.ProjectName,
        )
        if not lister:
            columns += (
                'Description',
                'Environment',
                'Disable Reason',
                'Global Cluster ID',
                'Global Cluster Name',
                'Project Display Name',
                'Workspace Display Name',
                'Shared Cluster ID',
                'Shared Cluster Name',
            )
            data = data + (
                mlapp.Description,
                mlapp.Environment,
                getattr(mlapp, 'DisableReason', '<none>'),
                getattr(mlapp, 'GlobalClusterID', '<none>'),
                getattr(mlapp, 'GlobalClusterName', '<none>'),
                mlapp.ProjectDisplayName,
                mlapp.WorkspaceDisplayName,
                getattr(mlapp, 'SharedClusterID', '<none>'),
                getattr(mlapp, 'SharedClusterName', '<none>'),
            )
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class List(base.DealerLister):
    """List all apps in the workspace."""

    def _get_format_function(self):
        return format_list

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)

        base.add_workspace_arg(parser)
        return parser

    @base.workspace_aware
    def _get_resources(self, args):
        dealer_client = self.app.client

        return dealer_client.apps.list(args.workspace)


class Get(show.ShowOne):
    """Show specific app."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument('name', help='App name.')

        return parser

    @base.workspace_aware
    def take_action(self, args):
        dealer_client = self.app.client
        mlapp = dealer_client.apps.get(args.workspace, args.name)

        return format(mlapp)


class GetConfig(command.Command):
    """Show specific app config."""

    def get_parser(self, prog_name):
        parser = super(GetConfig, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument('name', help='App name.')

        return parser

    @base.workspace_aware
    def take_action(self, args):
        dealer_client = self.app.client
        mlapp = dealer_client.apps.get(args.workspace, args.name)

        self.app.stdout.write(yaml.safe_dump(mlapp.Configuration))


class Delete(command.Command):
    """Delete app."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        base.add_workspace_arg(parser)

        parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion.'
        )

        parser.add_argument(
            'name',
            nargs='+',
            help='Name of app(s).'
        )

        return parser

    @base.workspace_aware
    def take_action(self, args):
        dealer_client = self.app.client

        utils.do_action_on_many(
            lambda s: dealer_client.apps.delete(
                args.workspace, s, args.force
            ),
            args.name,
            "Request to delete mlapp %s has been accepted.",
            "Unable to delete the specified mlapp(s)."
        )
