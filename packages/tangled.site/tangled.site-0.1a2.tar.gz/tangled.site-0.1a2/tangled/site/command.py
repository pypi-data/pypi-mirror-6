from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker

from tangled.abcs import ACommand

from .model import Base, Entry
from .model.user import User, Role, Permission


class Command(ACommand):

    @classmethod
    def configure(cls, parser):
        subparsers = parser.add_subparsers()
        init_db_parser = subparsers.add_parser('init_db')
        init_db_parser.add_argument('url')
        init_db_parser.add_argument('-u', '--username', default='admin')
        init_db_parser.add_argument(
            '-e', '--email', default='admin@example.com')
        init_db_parser.add_argument('-p', '--password', default='hunter2')
        init_db_parser.set_defaults(runner='init_db')

    def run(self):
        runner = getattr(self.args, 'runner', None)
        if runner:
            getattr(self, runner)()
        else:
            self.parser.print_help()

    def init_db(self):
        try:
            answer = input(
                'Are you sure you want to destroy existing data? '
                'Type "yes" to continue. ')
        except KeyboardInterrupt:
            self.exit('\nAborted.')

        if answer != 'yes':
            self.exit('Aborted.')

        username = self.args.username
        email = self.args.email
        password = self.args.password

        engine = create_engine(self.args.url)
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)()

        sudo_permission = Permission(key='sudo')

        sudo_role = Role(
            key='sudo',
            description='Superuser; can do *anything*',
            permissions=[sudo_permission],
        )

        user = User(
            username=username,
            email=email,
            password=password,
            roles=[sudo_role],
        )

        home_entry = Entry(
            slug='home',
            title='Home',
            content='This is the home page.',
            published=True,
            is_page=True,
        )

        entry = Entry(
            slug='an-entry',
            title='This is an entry',
            content='It contains some content',
            published=True,
        )

        session.add_all([user, home_entry, entry])
        session.commit()
        session.close()

        print(
            'Created superuser {}/{} with password {}'
            .format(username, email, password))
