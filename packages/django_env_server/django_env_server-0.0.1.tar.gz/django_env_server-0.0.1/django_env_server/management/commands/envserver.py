import os

from django.contrib.staticfiles.management.commands.runserver import Command as RunserverCommand

from django.conf import settings


class Command(RunserverCommand):

    def load_dotenv(self):

        def parse_dotenv(dotenv):
            for line in open(dotenv):
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, v = line.split('=', 1)
                v = v.strip("'").strip('"')
                yield k, v

        for k, v in parse_dotenv(settings.ENV_FILE):
            os.environ.setdefault(k, v)

    def handle(self, addrport='', *args, **options):
        self.load_dotenv()
        super(Command, self).handle(addrport='', *args, **options)
