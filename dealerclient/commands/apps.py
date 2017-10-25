import json
import yaml

from cliff import command
from cliff import show

from dealerclient.commands import base
from dealerclient.commands import charts
from dealerclient import exceptions
from dealerclient import utils


def format_list(app=None):
    return format(app, lister=True)


def format(app=None, lister=False):
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

    if app:
        data = (
            app.Name,
            app.DisplayName,
            app.Enabled,
            app.ClusterName,
            app.WorkspaceName,
            app.ProjectName,
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
                app.Description,
                app.Environment,
                getattr(app, 'DisableReason', '<none>'),
                getattr(app, 'GlobalClusterID', '<none>'),
                getattr(app, 'GlobalClusterName', '<none>'),
                app.ProjectDisplayName,
                app.WorkspaceDisplayName,
                getattr(app, 'SharedClusterID', '<none>'),
                getattr(app, 'SharedClusterName', '<none>'),
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


def format_config_task(app_task=None):
    columns = ('Name',)
    data = (app_task.name,)

    return columns, data


def format_source_list(source=None):
    return format_source(source, lister=True)


def format_source(source=None, lister=False):
    columns = ('Name', 'Mount path', 'SubPath', 'Lib', 'Train',)
    data = (
        source.name,
        source.mountPath,
        source.subPath,
        source.isLibDir,
        source.isTrainLogDir,
    )

    if not lister:
        # All below needed for dynamic column rendering.
        # Sources may have any new attributes in the future so
        # we can't refer to static field list.
        attrs = utils.get_public_attr(
            source,
            except_of=[
                'resource_name', 'defaults', 'manager', 'name', 'mountPath',
                'subPath', 'isLibDir', 'isTrainLogDir'
            ]
        )
        for k, v in attrs.items():
            columns += (k,)
            if isinstance(v, (list, dict)):
                v = json.dumps(v, indent=4)

            data += (v,)

    return columns, data


def format_status_list(status=None):
    return format_status(status, lister=True)


def format_status(status=None, lister=False):
    # {
    #     "name": "styles-set-jupyter",
    #     "reason": "",
    #     "resource_states": [
    #         {
    #             "events": [],
    #             "name": "styles-set-jupyter-3007719094-4m232",
    #             "status": "Running"
    #         }
    #     ],
    #     "status": "Running",
    #     "type": "UIX"
    # },
    columns = ('Name', 'Status', 'Type',)
    data = (
        status.name,
        status.status,
        status.type,
    )

    if not lister:
        columns += ('Reason', 'Resources',)
        data += (
            status.reason,
            json.dumps(status.resource_states, indent=4),
        )

    return columns, data


def format_packages_list(package=None):
    return format_package(package, lister=True)


def format_package(package=None, lister=False):
    # {
    #     "name": "styles-set-jupyter",
    #     "reason": "",
    #     "resource_states": [
    #         {
    #             "events": [],
    #             "name": "styles-set-jupyter-3007719094-4m232",
    #             "status": "Running"
    #         }
    #     ],
    #     "status": "Running",
    #     "type": "UIX"
    # },
    columns = ('Manager',)
    data = (
        package.manager,
    )

    if not lister:
        columns += ('Packages',)
        data += (
            '\n'.join(package.packages),
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
        app = dealer_client.apps.get(args.workspace, args.name)

        return format(app)


class PackageInstall(command.Command):
    """Show specific app."""

    def get_parser(self, prog_name):
        parser = super(PackageInstall, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument('name', help='App name.')
        parser.add_argument(
            '--manager',
            help='Package manager name.',
            default='pip2'
        )
        parser.add_argument(
            '--packages',
            help='Comma-separated list of packages.'
        )

        return parser

    @base.workspace_aware
    def take_action(self, args):
        dealer_client = self.app.client
        iterator = dealer_client.apps.packages_install(
            args.workspace,
            args.name,
            args.manager,
            args.packages.split(',')
        )

        first = next(iterator)
        self.app.stdout.write(first + '\n')

        for line in iterator:
            self.app.stdout.write(line + '\n')


class PackageList(base.DealerLister):
    """Show app status component list."""

    def _get_format_function(self):
        return format_packages_list

    def get_parser(self, prog_name):
        parser = super(PackageList, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument('name', help='App name.')

        return parser

    @base.workspace_aware
    def _get_resources(self, args):
        dealer_client = self.app.client
        packages = dealer_client.apps.packages_list(args.workspace, args.name)

        return packages


class PackageGet(show.ShowOne):
    """Show app status component list."""

    def get_parser(self, prog_name):
        parser = super(PackageGet, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument('app', help='App name.')
        parser.add_argument('--manager', help='Manager name.', default='pip2')
        parser.add_argument(
            '--all',
            help=(
                'Show all packages (if not, '
                'show only installed by the user).'
            ),
            action='store_true'
        )

        return parser

    @base.workspace_aware
    def take_action(self, args):
        dealer_client = self.app.client
        packages = dealer_client.apps.packages_list(
            args.workspace, args.app, args.all
        )

        for package in packages:
            if package.manager == args.manager:
                return format_package(package, lister=False)

        raise exceptions.DealerClientException(
            'Manager "%s" not found in package manager list.' % args.manager
        )


class StatusList(base.DealerLister):
    """Show app status component list."""

    def _get_format_function(self):
        return format_status_list

    def get_parser(self, prog_name):
        parser = super(StatusList, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument('name', help='App name.')

        return parser

    @base.workspace_aware
    def _get_resources(self, args):
        dealer_client = self.app.client
        status = dealer_client.apps.status(args.workspace, args.name)

        return status


class StatusGet(show.ShowOne):
    """Show app status component list."""

    def get_parser(self, prog_name):
        parser = super(StatusGet, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument('app', help='App name.')
        parser.add_argument('name', help='Component name.')

        return parser

    @base.workspace_aware
    def take_action(self, args):
        dealer_client = self.app.client
        statuses = dealer_client.apps.status(args.workspace, args.app)

        for status in statuses:
            if status.name == args.name:
                return format_status(status, lister=False)

        raise exceptions.DealerClientException(
            'Component "%s" not found in status list.' % args.name
        )


class Disable(show.ShowOne):
    """Show specific app."""

    def get_parser(self, prog_name):
        parser = super(Disable, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument('name', help='App name.')

        return parser

    @base.workspace_aware
    def take_action(self, args):
        dealer_client = self.app.client
        app = dealer_client.apps.disable(args.workspace, args.name)

        return format(app)


class Enable(show.ShowOne):
    """Show specific app."""

    def get_parser(self, prog_name):
        parser = super(Enable, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument('name', help='App name.')

        return parser

    @base.workspace_aware
    def take_action(self, args):
        dealer_client = self.app.client
        app = dealer_client.apps.enable(args.workspace, args.name)

        return format(app)


class ConfigTasks(base.DealerLister):
    """List tasks defined in app config."""

    def _get_format_function(self):
        return format_config_task

    def get_parser(self, prog_name):
        parser = super(ConfigTasks, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument('name', help='App name.')

        return parser

    @base.workspace_aware
    def _get_resources(self, args):
        dealer_client = self.app.client
        app = dealer_client.apps.get(args.workspace, args.name)
        tasks = app.get_config_tasks()

        return tasks


class ConfigTask(show.ShowOne):
    """Show specific task from app config."""

    def get_parser(self, prog_name):
        parser = super(ConfigTask, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument('app', help='App name.')
        parser.add_argument('name', help='Task name.')

        return parser

    @base.workspace_aware
    def take_action(self, args):
        dealer_client = self.app.client
        app = dealer_client.apps.get(args.workspace, args.app)

        t = app.get_config_task(args.name)
        self.app.stdout.write(yaml.safe_dump(t.to_dict()))
        self.app.stdout.write('\n')


class Upload(command.Command):
    """Upload a file to specific source of the app."""

    def get_parser(self, prog_name):
        parser = super(Upload, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument('name', help='App name.')
        parser.add_argument('--source', required=True, help='Source name.')
        parser.add_argument('--file', help='File path.')

        return parser

    @base.workspace_aware
    def take_action(self, args):
        dealer_client = self.app.client
        app = dealer_client.apps.get(args.workspace, args.name)

        resp = app.upload_file(args.source, args.file)
        self.app.stdout.write(resp)
        self.app.stdout.write('\n')


class ListSources(base.DealerLister):
    """List all app sources."""

    def _get_format_function(self):
        return format_source_list

    def get_parser(self, prog_name):
        parser = super(ListSources, self).get_parser(prog_name)

        base.add_workspace_arg(parser)
        parser.add_argument('name', help='App name.')
        return parser

    @base.workspace_aware
    def _get_resources(self, args):
        dealer_client = self.app.client

        app = dealer_client.apps.get(args.workspace, args.name)

        return app.get_sources()


class GetSource(show.ShowOne):
    """Show specific app source."""

    def get_parser(self, prog_name):
        parser = super(GetSource, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument('name', help='App name.')
        parser.add_argument('source', help='Source name.')

        return parser

    @base.workspace_aware
    def take_action(self, args):
        dealer_client = self.app.client
        app = dealer_client.apps.get(args.workspace, args.name)

        sources = app.get_sources()
        found = None
        for source in sources:
            if source.name == args.source:
                found = source

        if not found:
            raise exceptions.DealerClientException(
                'App source [name=%s] not found.' % args.source
            )

        return format_source(found)


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
    """Get specific app destination by name."""

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
        app = dealer_client.apps.get(args.workspace, args.name)

        self.app.stdout.write(yaml.safe_dump(app.Configuration))


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
            "Request to delete app %s has been accepted.",
            "Unable to delete the specified app(s)."
        )
