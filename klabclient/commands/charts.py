import json
import textwrap
import yaml

from cliff import command
from cliff import show
from six import moves

from klabclient.commands import base
from klabclient import utils


urllib = moves.urllib.request


def format_list(chart=None):
    return format(chart, lister=True)


def format(chart=None, lister=False):
    print(chart)
    # "ID": "2651",
    # "Name": "zappos-ui",
    # "Interface": "app",
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
        'Interface',
        'Version',
        'Workspace',
    )

    if chart:
        data = (
            chart.ID,
            chart.Name,
            chart.DisplayName,
            chart.Interface,
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
                '\n'.join(textwrap.wrap(getattr(chart, 'Picture', ''), 90)),
                chart.Published,
                chart.RepositoryID,
                chart.RepositoryURL,
                chart.RepositoryDir,
                chart.Comments,
                chart.Stars,
                chart.Star,
                chart.InstallConfig,
                chart.Keywords,
                json.dumps(getattr(chart, 'Info', {}), indent=4),
                chart.Broken,
                chart.DownloadURL,
            )
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


def format_version(v=None):
    columns = ('Version',)
    data = (v.Version,)

    return columns, data


class Catalog(base.KuberlabLister):
    """List charts using catalog."""

    def _get_format_function(self):
        return format_list

    @property
    def _catalog_function(self):
        klab_client = self.app.client
        return klab_client.charts.catalog

    def get_parser(self, prog_name):
        parser = super(Catalog, self).get_parser(prog_name)

        parser.add_argument(
            '--search',
            help='Elastic search by specified string.'
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
        return self._catalog_function(
            args.search,
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
        klab_client = self.app.client

        return klab_client.charts.list(
            args.workspace,
            args.search,
            args.page,
            args.limit
        )


class ListVersions(base.KuberlabLister):
    """List charts in the specific workspace."""

    @property
    def _action_function(self):
        klab_client = self.app.client

        return klab_client.charts.list_versions

    def _get_format_function(self):
        return format_version

    def get_parser(self, prog_name):
        parser = super(ListVersions, self).get_parser(prog_name)

        base.add_workspace_arg(parser)
        parser.add_argument(
            'name',
            help='Chart name.'
        )
        return parser

    @base.workspace_aware
    def _get_resources(self, args):
        return self._action_function(
            args.workspace,
            args.name
        )


class Get(show.ShowOne):
    """Get specific chart by name."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument(
            '--chart-version',
            dest='version',
            help='Chart version.'
        )
        parser.add_argument(
            'name',
            help='Chart name.'
        )

        return parser

    @base.workspace_aware
    def take_action(self, args):
        klab_client = self.app.client
        chart = klab_client.charts.get(
            args.workspace, args.name, args.version
        )

        return format(chart)


class GetValues(command.Command):
    """Get specific chart values yaml."""

    @property
    def _action_function(self):
        client = self.app.client
        return client.apps.get_values

    def get_parser(self, prog_name):
        parser = super(GetValues, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument(
            '--chart-version',
            dest='version',
            default='latest',
            help='Version.'
        )
        parser.add_argument(
            'name',
            help='Name.'
        )

        return parser

    @base.workspace_aware
    def take_action(self, args):
        values = self._action_function(
            args.workspace, args.name, args.version
        )

        self.app.stdout.write(values)
        self.app.stdout.write('\n')


class GetYaml(command.Command):
    """Get Chart.yaml."""

    @property
    def _action_function(self):
        client = self.app.client
        return client.apps.get_yaml

    def get_parser(self, prog_name):
        parser = super(GetYaml, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument(
            '--chart-version',
            dest='version',
            default='latest',
            help='Version.'
        )
        parser.add_argument(
            'name',
            help='Name.'
        )

        return parser

    @base.workspace_aware
    def take_action(self, args):
        chart_yaml = self._action_function(
            args.workspace, args.name, args.version
        )

        self.app.stdout.write(chart_yaml)
        self.app.stdout.write('\n')


class Download(command.Command):
    """Download chart to the specific location."""

    def get_parser(self, prog_name):
        parser = super(Download, self).get_parser(prog_name)

        base.add_workspace_arg(parser)
        parser.add_argument(
            '--chart-version',
            dest='version',
            help='Chart version.'
        )
        parser.add_argument(
            '--output',
            '-o',
            help='Output file name.'
        )

        parser.add_argument(
            'name',
            help='Chart name.'
        )

        return parser

    @base.workspace_aware
    def take_action(self, args):
        klab_client = self.app.client
        chart = klab_client.charts.get(
            args.workspace, args.name, args.version
        )

        url = chart.DownloadURL
        output = args.output
        if not output:
            output = url.split('?')[0].split('/')[-1]

        self.app.stdout.write('Saving %s to %s..\n' % (url, output))
        downloader = urllib.URLopener()
        downloader.retrieve(url, output)
        self.app.stdout.write('Done.\n')


class Create(show.ShowOne):
    """Create a new chart from repository."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument(
            '--name',
            required=True,
            help='New chart name.'
        )
        parser.add_argument(
            '--repo-url',
            required=True,
            help='Chart source repository URL.'
        )
        parser.add_argument(
            '--repo-dir',
            help='Chart source repository Dir.'
        )

        return parser

    @base.workspace_aware
    def take_action(self, args):
        klab_client = self.app.client
        chart = klab_client.charts.create(
            args.workspace, args.name, args.repo_url, args.repo_dir
        )

        return format(chart)


class Install(show.ShowOne):
    """Install a new chart on cluster."""

    def get_parser(self, prog_name):
        parser = super(Install, self).get_parser(prog_name)

        parser.add_argument(
            '--name',
            required=True,
            help='Chart name.'
        )
        parser.add_argument(
            '--chart-workspace',
            required=True,
            help='Chart workspace name.'
        )
        parser.add_argument(
            '--target-workspace',
            required=True,
            help='Target workspace name.'
        )
        parser.add_argument(
            '--project',
            help='Project name.'
        )
        parser.add_argument(
            '--target-application',
            '-app',
            required=True,
            help='New application name.'
        )
        parser.add_argument(
            '--chart-version',
            default='latest',
            help='Target chart version.'
        )
        parser.add_argument(
            '--cluster-name',
            help='Target cluster name.'
        )
        parser.add_argument(
            '--shared-cluster-id',
            help='Target shared cluster id.'
        )
        parser.add_argument(
            '--cluster-id',
            help='Target cluster id.'
        )
        parser.add_argument(
            '--env',
            default='master',
            help='Project environment (repo branch).'
        )
        parser.add_argument(
            '--values',
            # default='values.yaml',
            help='Path to values.yaml.'
        )

        return parser

    @property
    def _install_function(self):
        klab_client = self.app.client
        return klab_client.charts.install

    @base.workspace_aware
    def take_action(self, args):

        values = None
        if args.values:
            with open(args.values) as f:
                values = yaml.safe_load(f)

        # from_workspace, to_workspace, chart_name,
        #        project, app_name, values, version='latest',
        #        cluster_name=None, shared_cluster_id=None, env="master"
        app = self._install_function(
            args.chart_workspace,
            args.target_workspace,
            args.name,
            args.target_application,
            values,
            args.project,
            args.chart_version,
            args.cluster_name,
            args.shared_cluster_id,
            args.cluster_id,
            args.env,
        )

        return format(app)


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
        klab_client = self.app.client

        utils.do_action_on_many(
            lambda s: klab_client.charts.delete(args.workspace, s),
            args.name,
            "Request to delete chart %s has been accepted.",
            "Unable to delete the specified chart(s)."
        )
