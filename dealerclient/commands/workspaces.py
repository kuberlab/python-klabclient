
import argparse
import json

from cliff import command
from cliff import show

from dealerclient.commands import base
from dealerclient import utils


def format_list(workspace=None):
    return format(workspace, lister=True)


def format(workspace=None, lister=False):
    columns = (
        'Name',
        'Type',
        'Display name',
        'Picture'
    )

    if workspace:
        data = (
            workspace.Name,
            workspace.Type,
            workspace.DisplayName,
            #
            workspace.Picture
        )
        if not lister:
            columns += ('Can',)
            data = data + (json.dumps(workspace.Can, indent=4),)
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class List(base.DealerLister):
    """List all workspaces."""

    def _get_format_function(self):
        return format_list

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)

        return parser

    def _get_resources(self, parsed_args):
        dealer_client = self.app.client

        return dealer_client.workspaces.list()


class Get(show.ShowOne):
    """Show specific workspace."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument('workspace', help='Workspace name.')

        return parser

    def take_action(self, parsed_args):
        dealer_client = self.app.client
        ws = dealer_client.workspaces.get(parsed_args.workspace)

        return format(ws)


class Create(base.DealerLister):
    """Create new workspace."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument(
            'definition',
            type=argparse.FileType('r'),
            help='Workspace definition file.'
        )

        return parser

    def _get_format_function(self):
        return format_list

    def _validate_parsed_args(self, parsed_args):
        if not parsed_args.definition:
            raise RuntimeError("You must provide path to workspace "
                               "definition file.")

    def _get_resources(self, parsed_args):
        scope = 'public' if parsed_args.public else 'private'
        dealer_client = self.app.client_manager.workspace_engine

        return dealer_client.workspaces.create(
            parsed_args.definition.read(),
            scope=scope
        )


class Delete(command.Command):
    """Delete workspace."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument(
            'workspace',
            nargs='+',
            help='Name or ID of workspace(s).'
        )

        return parser

    def take_action(self, parsed_args):
        dealer_client = self.app.client
        utils.do_action_on_many(
            lambda s: dealer_client.workspaces.delete(s),
            parsed_args.workspace,
            "Request to delete workspace %s has been accepted.",
            "Unable to delete the specified workspace(s)."
        )


class Update(base.DealerLister):
    """Update workspace."""

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)

        parser.add_argument(
            'definition',
            type=argparse.FileType('r'),
            help='Workspace definition'
        )
        parser.add_argument('--id', help='Workspace ID.')

        return parser

    def _get_format_function(self):
        return format_list

    def _get_resources(self, parsed_args):
        dealer_client = self.app.client

        return dealer_client.workspaces.update(
            parsed_args.definition.read(),
            id=parsed_args.id
        )
