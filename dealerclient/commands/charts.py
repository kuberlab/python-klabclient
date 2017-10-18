from cliff import command
from cliff import show

from dealerclient.commands import base
from dealerclient import utils


def format_list(chart=None):
    return format(chart, lister=True)


def format(chart=None, lister=False):
    # "ID": "2651",
    # "Name": "zappos-ui",
    # "Type": "app",
    # "Version": "1.0.0",
    # "DisplayName": "zappos-ui",
    # "Description": "Zappos UI Demo",
    # "Picture": "",
    # "Published": true,
    # "RepositoryID": "2651",
    # "RepositoryURL": "https://github.com/kuberlab-catalog/zappos-ui",
    # "RepositoryDir": "/",
    # "Comments": 0,
    # "Stars": 0,
    # "Star": false,
    # "InstallConfig": {
    #                      "ClusterStorage": false
    #                  },
    # "Keywords": [
    #                 "kubernets",
    #                 "demo",
    #                 "zappos"
    #             ],
    # "Info": {},
    # "Broken": false,
    # "DownloadURL": "",
    # "WorkspaceName": "kuberlab-demo",
    # "WorkspaceDisplayName": "KuberLab Demo"
    columns = (
        'ID',
        'Name',
        'Display name',
        'Type',
        'Version',
        'Workspace',
    )

    if chart:
        data = (
            chart.ID,
            chart.Name,
            chart.DisplayName,
            chart.Type,
            chart.Version,
            chart.WorkspaceName,
        )
        if not lister:
            columns += (
                'Description',
                'Picture',
                'Published',
                'Repository ID',
                'Repository URL',
                'Repository Dir',
                'Comments',
                'Stars',
                'Star',
                'Install config',
                'Keywords',
                'Info',
                'Broken',
                'Download URL',
            )
            data = data + (
                chart.Description,
                chart.Picture,
                chart.Published,
                chart.RepositoryID,
                chart.RepositoryURL,
                chart.RepositoryDir,
                chart.Comments,
                chart.Stars,
                chart.Star,
                chart.InstallConfig,
                chart.Keywords,
                chart.Info,
                chart.Broken,
                chart.DownloadURL,
            )
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class Catalog(base.DealerLister):
    """List charts using catalog."""

    def _get_format_function(self):
        return format_list

    def get_parser(self, prog_name):
        parser = super(Catalog, self).get_parser(prog_name)

        parser.add_argument(
            '--search',
            help='Elastic search by specified string.'
        )
        parser.add_argument(
            '--type',
            default='mlapp-v2',
            choices=['app', 'mlapp-v2'],
            help='Filter by type.'
        )
        parser.add_argument(
            '--page',
            metavar='<int>',
            help='Request specified page.'
        )
        parser.add_argument(
            '--limit',
            metavar='<int>',
            default=10,
            help='Limit response.'
        )
        return parser

    def _get_resources(self, args):
        dealer_client = self.app.client

        return dealer_client.charts.catalog(
            args.search,
            args.type,
            args.page,
            args.limit
        )


class List(Catalog):
    """List charts in the specific workspace."""

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)

        base.add_workspace_arg(parser)
        return parser

    @base.workspace_aware
    def _get_resources(self, args):
        dealer_client = self.app.client

        return dealer_client.charts.list(
            args.workspace,
            args.search,
            args.type,
            args.page,
            args.limit
        )


class Get(show.ShowOne):
    """Get specific chart by name."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument(
            'name',
            help='Chart name.'
        )

        return parser

    @base.workspace_aware
    def take_action(self, args):
        dealer_client = self.app.client
        chart = dealer_client.charts.get(args.workspace, args.name)

        return format(chart)


class Delete(command.Command):
    """Delete chart."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        base.add_workspace_arg(parser)

        parser.add_argument(
            'name',
            nargs='+',
            help='Name of chart(s).'
        )

        return parser

    @base.workspace_aware
    def take_action(self, args):
        dealer_client = self.app.client

        utils.do_action_on_many(
            lambda s: dealer_client.charts.delete(args.workspace, s),
            args.name,
            "Request to delete chart %s has been accepted.",
            "Unable to delete the specified chart(s)."
        )
