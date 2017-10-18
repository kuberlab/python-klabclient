import json
import yaml

from cliff import command
from cliff import show

from dealerclient.commands import base
from dealerclient.commands import charts
from dealerclient import exceptions
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


def format_dest_list(dest=None):
    return format_destination(dest, lister=True)


def format_destination(dest=None, lister=False):
    columns = ('Type', 'Name', 'ID',)
    data = (dest.Type, dest.Name, dest.ID,)

    if not lister:
        columns += ('Meta',)
        data += (
            json.dumps(getattr(dest, 'Meta', {}), indent=4),
        )

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


class ListDestinations(base.DealerLister):
    """List app destinations (project and clusters)."""

    def _get_format_function(self):
        return format_dest_list

    def get_parser(self, prog_name):
        parser = super(ListDestinations, self).get_parser(prog_name)
        base.add_workspace_arg(parser)

        return parser

    @base.workspace_aware
    def _get_resources(self, args):
        dealer_client = self.app.client
        dest = dealer_client.apps.get_destinations(args.workspace)

        return dest


class GetDestination(show.ShowOne):
    """Get specific chart by name."""

    def get_parser(self, prog_name):
        parser = super(GetDestination, self).get_parser(prog_name)
        base.add_workspace_arg(parser)

        parser.add_argument(
            '--type',
            required=True,
            help='Destination type.'
        )
        parser.add_argument(
            '--id',
            required=True,
            help='Destination id.'
        )

        return parser

    @base.workspace_aware
    def take_action(self, args):
        dealer_client = self.app.client
        dests = dealer_client.apps.get_destinations(args.workspace)

        found = None
        for dest in dests:
            if dest.Type == args.type and dest.ID == args.id:
                found = dest

        if not found:
            raise exceptions.DealerClientException(
                'App destination [Type=%s, ID=%s] not found.'
                % (args.type, args.id)
            )
        return format_destination(found)


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


class Install(charts.Install):
    pass


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
