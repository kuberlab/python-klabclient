import json

from cliff import command
from cliff import show

from klabclient.commands import base
from klabclient.commands import charts
from klabclient import utils


def format_list(model=None):
    return format(model, lister=True)


def format(model=None, lister=False):
    # "ID": "655",
    # "Name": "ct-cancer",
    # "DisplayName": "CT Cancer",
    # "Description": "LUng Nodule Analysis",
    # "Keywords": [],
    # "Published": true,
    # "Comments": 0,
    # "Stars": 1,
    # "Star": false,
    # "Picture": "/file/mmpic/4811/cancer.png",
    # "WorkspaceName": "kuberlab-demo",
    # "WorkspaceDisplayName": "KuberLab Demo",
    columns = (
        'ID',
        'Name',
        'Display name',
        'Published',
        'Workspace name',
    )

    if model:
        data = (
            model.ID,
            model.Name,
            model.DisplayName,
            model.Published,
            model.WorkspaceName
        )
        if not lister:
            columns += ('Description', 'Keywords', 'Picture',)
            data = data + (
                model.Description,
                json.dumps(model.Keywords, indent=4),
                model.Picture if hasattr(model, 'Picture') else None,
            )
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class Catalog(charts.Catalog):
    @property
    def _catalog_function(self):
        client = self.app.client
        return client.models.catalog

    def _get_format_function(self):
        return format_list


class List(base.KuberlabLister):
    """List all models in the workspace."""

    def _get_format_function(self):
        return format_list

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)

        base.add_workspace_arg(parser)
        return parser

    @base.workspace_aware
    def _get_resources(self, args):
        klab_client = self.app.client

        return klab_client.models.list(args.workspace)


class Get(show.ShowOne):
    """Show specific model."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument('name', help='Model name.')

        return parser

    @base.workspace_aware
    def take_action(self, args):
        klab_client = self.app.client
        model = klab_client.models.get(args.workspace, args.name)

        return format(model)


class Create(show.ShowOne):
    """Create new model."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        # workspace, name, display_name=None,
        # picture=None
        base.add_workspace_arg(parser)
        parser.add_argument(
            '--name',
            required=True,
            help='Model name.'
        )
        parser.add_argument(
            '--display-name',
            help='Display name.',
            nargs='?'
        )
        parser.add_argument(
            '--picture',
            help='Picture URL.',
            nargs='?'
        )
        parser.add_argument(
            '--publish',
            help='With this flag model will be public.',
            action='store_true'
        )

        return parser

    @base.workspace_aware
    def take_action(self, args):
        klab_client = self.app.client
        model = klab_client.models.create(
            args.workspace,
            args.name,
            display_name=args.display_name,
            picture=args.picture,
            published=args.publish,
        )

        return format(model)


class Delete(command.Command):
    """Delete model."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        base.add_workspace_arg(parser)

        parser.add_argument(
            'name',
            nargs='+',
            help='Name of model(s).'
        )

        return parser

    @base.workspace_aware
    def take_action(self, args):
        klab_client = self.app.client

        utils.do_action_on_many(
            lambda s: klab_client.models.delete(args.workspace, s),
            args.name,
            "Request to delete model %s has been accepted.",
            "Unable to delete the specified model(s)."
        )


class Upload(show.ShowOne):
    """Upload model."""

    def get_parser(self, prog_name):
        parser = super(Upload, self).get_parser(prog_name)
        base.add_workspace_arg(parser)
        parser.add_argument('name', help='Name of model.')
        parser.add_argument('version', help='Model version.')
        parser.add_argument(
            'path',
            help=(
                'Path to model. It is either '
                '.tar.gz file or path to directory.'
            )
        )

        return parser

    @base.workspace_aware
    def take_action(self, args):
        klab_client = self.app.client

        m = klab_client.models.upload(
            args.workspace, args.name, args.version, args.path
        )

        return format(m)


class Update(show.ShowOne):
    """Update model."""

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)
        # workspace, name, description=None, display_name=None, keywords=None
        base.add_workspace_arg(parser)
        parser.add_argument(
            '--name',
            required=True,
            help='Model name.'
        )
        parser.add_argument(
            '--description',
            help='Description of the model.',
            nargs='?'
        )
        parser.add_argument(
            '--display-name',
            help='Display name.',
            nargs='?'
        )
        parser.add_argument(
            '--keyword',
            help='Keyword. Arg can be multiplied.',
            nargs='+'
        )

        return parser

    @base.workspace_aware
    def take_action(self, args):
        klab_client = self.app.client
        model = klab_client.models.update(
            args.workspace,
            args.name,
            display_name=args.display_name,
            description=args.description,
            keywords=args.keyword,
        )

        return format(model)
