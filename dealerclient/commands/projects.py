from cliff import command
from cliff import show

from dealerclient.commands import base
from dealerclient import utils


def format_list(project=None):
    return format(project, lister=True)


def format(project=None, lister=False):
    # "ID": "4121",
    # "Name": "go-kuberlab",
    # "DisplayName": "go.kuberlab",
    # "Description": "",
    # "Environment": "master",
    # "RepositoryID": "2041",
    # "RepositoryURL": "https://github.com/kuberlab/go.kuberlab",
    # "RepositoryDir": "/"
    columns = (
        'ID',
        'Name',
        'Display name',
        'Repository URL',
        'Environment',
    )

    if project:
        data = (
            project.ID,
            project.Name,
            project.DisplayName,
            project.RepositoryURL,
            project.Environment
        )
        if not lister:
            columns += ('Description', 'Repository ID', 'Repository Dir',)
            data = data + (
                project.Description,
                project.RepositoryID,
                project.RepositoryDir,
            )
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class List(base.DealerLister):
    """List all projects."""

    def _get_format_function(self):
        return format_list

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)

        parser.add_argument(
            '--workspace',
            required=True,
            help='Workspace name to search projects in.'
        )
        return parser

    def _get_resources(self, args):
        dealer_client = self.app.client

        return dealer_client.projects.list(args.workspace)


class Get(show.ShowOne):
    """Show specific project."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)
        parser.add_argument(
            '--workspace',
            required=True,
            help='Workspace name to search projects in.'
        )
        parser.add_argument('name', help='Project name.')

        return parser

    def take_action(self, args):
        dealer_client = self.app.client
        project = dealer_client.projects.get(args.workspace, args.name)

        return format(project)


class Create(show.ShowOne):
    """Create new project."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        # workspace, name, display_name=None,
        # env=None, repo_url=None, repo_dir=None
        parser.add_argument(
            '--workspace',
            required=True,
            help='Workspace name.'
        )
        parser.add_argument(
            '--name',
            required=True,
            help='Project name.'
        )
        parser.add_argument(
            '--repo-url',
            required=True,
            help='Repository url.',
            nargs='?'
        )
        parser.add_argument(
            '--env',
            required=True,
            help='Repository branch.',
            nargs='?'
        )
        parser.add_argument(
            '--repo-dir',
            help='Repository path dir.',
            nargs='?'
        )
        parser.add_argument(
            '--display-name',
            help='Display name.',
            nargs='?'
        )

        return parser

    def take_action(self, args):
        dealer_client = self.app.client
        project = dealer_client.projects.create(
            args.workspace,
            args.name,
            display_name=args.display_name,
            repo_url=args.repo_url,
            env=args.env,
            repo_dir=args.repo_dir,
        )

        return format(project)


class Delete(command.Command):
    """Delete project."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument(
            '--workspace',
            required=True,
            help='Workspace name.'
        )

        parser.add_argument(
            'name',
            nargs='+',
            help='Name of project(s).'
        )

        return parser

    def take_action(self, args):
        dealer_client = self.app.client

        utils.do_action_on_many(
            lambda s: dealer_client.projects.delete(args.workspace, s),
            args.name,
            "Request to delete project %s has been accepted.",
            "Unable to delete the specified project(s)."
        )


class Update(show.ShowOne):
    """Update project."""

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)
        # name, display_name=None, picture=None, url=None, phone=None
        parser.add_argument(
            '--workspace',
            required=True,
            help='Workspace name.'
        )
        parser.add_argument(
            '--name',
            required=True,
            help='Project name.'
        )
        parser.add_argument(
            '--repo-url',
            required=True,
            help='Repository url.',
            nargs='?'
        )
        parser.add_argument(
            '--env',
            required=True,
            help='Repository branch.',
            nargs='?'
        )
        parser.add_argument(
            '--repo-dir',
            help='Repository path dir.',
            nargs='?'
        )
        parser.add_argument(
            '--display-name',
            help='Display name.',
            nargs='?'
        )

        return parser

    def take_action(self, args):
        dealer_client = self.app.client
        project = dealer_client.projects.update(
            args.workspace,
            args.name,
            display_name=args.display_name,
            repo_url=args.repo_url,
            env=args.env,
            repo_dir=args.repo_dir,
        )

        return format(project)
