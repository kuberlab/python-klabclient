from cliff import command
from cliff import show

from klabclient.commands import base


def format_list(org=None):
    return format(org, lister=True)


def format(org=None, lister=False):
    # "ID": "2",
    # "Name": "kuberlab",
    # "DisplayName": "kuberlab",
    # "Url": "",
    # "Phone": "",
    # "Picture": "/1234567/icons/def/org.svg",
    # "Workspace": "kuberlab",
    # "WorkspaceName": "kuberlab"
    columns = (
        'ID',
        'Name',
        'Display name',
        'Picture',
    )

    if org:
        data = (
            org.ID,
            org.Name,
            org.DisplayName,
            org.Picture
        )
        if not lister:
            columns += ('Url', 'Phone', 'Workspace', 'Workspace name')
            data = data + (
                org.Url,
                org.Phone,
                org.Workspace,
                org.WorkspaceName,
            )
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class List(base.KuberlabLister):
    """List all organizations."""

    def _get_format_function(self):
        return format_list

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)

        return parser

    def _get_resources(self, parsed_args):
        klab_client = self.app.client

        return klab_client.organizations.list()


class Get(show.ShowOne):
    """Show specific organization."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument('id', help='Organization ID.')

        return parser

    def take_action(self, parsed_args):
        klab_client = self.app.client
        org = klab_client.organizations.get(parsed_args.id)

        return format(org)


class Create(show.ShowOne):
    """Create new organization."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        # name, display_name=None, picture=None, url=None, phone=None
        parser.add_argument(
            'name',
            help='Organization name.'
        )
        parser.add_argument(
            '--display-name',
            help='Organization display name.',
            nargs='?'
        )
        parser.add_argument(
            '--picture',
            help='Organization picture url.',
            nargs='?'
        )
        parser.add_argument(
            '--url',
            help='Organization url.',
            nargs='?'
        )
        parser.add_argument(
            '--phone',
            help='Organization phone.',
            nargs='?'
        )

        return parser

    def take_action(self, args):
        klab_client = self.app.client
        org = klab_client.organizations.create(
            args.name,
            display_name=args.display_name,
            picture=args.picture,
            url=args.url,
            phone=args.phone
        )

        return format(org)


class Delete(command.Command):
    """Delete organization."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument(
            'id',
            help='ID of organization(s).'
        )

        parser.add_argument(
            '--confirm',
            help=(
                'Confirmation string to delete the org. '
                '(Usually this is org\'s name)'
            )
        )

        return parser

    def take_action(self, args):
        klab_client = self.app.client

        klab_client.organizations.delete(args.id, args.confirm)
        self.app.stdout.write('Request for deletion has accepted.\n')


class Update(show.ShowOne):
    """Update organization."""

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)
        # name, display_name=None, picture=None, url=None, phone=None
        parser.add_argument(
            'name',
            help='Organization name.'
        )
        parser.add_argument(
            '--display-name',
            help='Organization display name.',
            nargs='?'
        )
        parser.add_argument(
            '--picture',
            help='Organization picture url.',
            nargs='?'
        )
        parser.add_argument(
            '--url',
            help='Organization url.',
            nargs='?'
        )
        parser.add_argument(
            '--phone',
            help='Organization phone.',
            nargs='?'
        )

        return parser

    def take_action(self, args):
        klab_client = self.app.client
        org = klab_client.organizations.update(
            args.name,
            display_name=args.display_name,
            picture=args.picture,
            url=args.url,
            phone=args.phone
        )

        return format(org)
