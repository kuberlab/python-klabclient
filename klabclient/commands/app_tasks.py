
from cliff import command
from cliff import show

from klabclient.commands import base


def format_list(app_task=None):
    return format(app_task, lister=True)


def format(app_task=None, lister=False):
    # "app": "21-styles-set",
    # "build": "7",
    # "completed": false,
    # "config": "labels: null\nname: prepare-data\n...",
    # "name": "prepare-data",
    # "serve": null,
    # "start_time": "2017-10-19T13:06:01.543311498Z",
    # "status": "Starting",
    # "stop_time": null,
    # "exitError": "",
    columns = (
        'App',
        'Name',
        'Build',
        'Status',
        'Completed',
    )

    if app_task:
        data = (
            app_task.app,
            app_task.name,
            app_task.build,
            app_task.status,
            app_task.completed,

        )
        if not lister:
            columns += ('Exit error', 'Start', 'Stop',)
            data += (
                app_task.start_time,
                app_task.stop_time,
                getattr(app_task, 'exitError', None),
            )
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


def format_pod(pod=None):
    columns = ('Name', 'Status')
    data = (pod.Name, pod.Status,)

    return columns, data


class List(base.KuberlabLister):
    """List all app_tasks in the workspace."""

    def _get_format_function(self):
        return format_list

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)

        base.add_workspace_arg(parser)
        parser.add_argument('app', help='App name.')
        return parser

    @base.workspace_aware
    def _get_resources(self, args):
        klab_client = self.app.client

        return klab_client.app_tasks.list(args.workspace, args.app)


class Get(show.ShowOne):
    """Show specific app_task."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument('app', help='App name.')
        parser.add_argument('name', help='Task name.')
        parser.add_argument('build', help='Build name.')

        return parser

    @base.workspace_aware
    def take_action(self, args):
        klab_client = self.app.client
        app_task = klab_client.app_tasks.get(
            args.workspace, args.app, args.name, args.build
        )

        return format(app_task)


class GetPods(base.KuberlabLister):
    """Show specific app_task."""

    def _get_format_function(self):
        return format_pod

    def get_parser(self, prog_name):
        parser = super(GetPods, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument('app', help='App name.')
        parser.add_argument('name', help='Task name.')
        parser.add_argument('build', help='Build name.')

        return parser

    @base.workspace_aware
    def _get_resources(self, args):
        klab_client = self.app.client
        pods = klab_client.app_tasks.get_pods(
            args.workspace, args.app, args.name, args.build
        )

        return pods


class GetLogs(command.Command):
    """Show specific app_task."""

    def get_parser(self, prog_name):
        parser = super(GetLogs, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument('app', help='App name.')
        parser.add_argument('name', help='Task name.')
        parser.add_argument('build', help='Build name.')
        parser.add_argument('pod', help='Pod name.')

        return parser

    @base.workspace_aware
    def take_action(self, args):
        klab_client = self.app.client
        logs = klab_client.app_tasks.get_pod_logs(
            args.workspace, args.app, args.name, args.build, args.pod
        )

        self.app.stdout.write(logs)
        self.app.stdout.write('\n')


class Delete(command.Command):
    """Delete app_task."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        base.add_workspace_arg(parser)

        parser.add_argument('app', help='App name.')
        parser.add_argument('name', help='Task name.')
        parser.add_argument('build', help='Build name.')

        return parser

    @base.workspace_aware
    def take_action(self, args):
        klab_client = self.app.client

        klab_client.app_tasks.delete(
            args.workspace,
            args.app,
            args.name,
            args.build
        )
        self.app.stdout.write('Ok.\n')


class Run(show.ShowOne):
    """Run app task."""

    def get_parser(self, prog_name):
        parser = super(Run, self).get_parser(prog_name)
        # name, display_name=None, picture=None, url=None, phone=None
        base.add_workspace_arg(parser)
        parser.add_argument('app', help='App name.')
        parser.add_argument('name', help='Task name.')

        parser.add_argument(
            '--wait',
            help='Wait until task completed.',
            action='store_true'
        )
        parser.add_argument(
            '--watch',
            help='Print task status in stdout every ~3 sec.',
            action='store_true'
        )

        return parser

    @base.workspace_aware
    def take_action(self, args):
        klab_client = self.app.client
        app = klab_client.apps.get(args.workspace, args.app)

        task = app.get_config_task(args.name)
        task.start()

        if args.wait:
            task_callback = None
            if args.watch:
                def task_callback(t):
                    self.app.stdout.write(
                        '%s\n' % t
                    )
            task.wait(tick_callback=task_callback)

        return format(task)
