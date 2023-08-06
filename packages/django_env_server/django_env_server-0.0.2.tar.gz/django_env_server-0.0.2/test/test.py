import os

from django.utils import unittest

from django.core.management import load_command_class
from django.core.management.base import BaseCommand


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')


class TestEnvServerCommand(unittest.TestCase):

    def setUp(self):
        self.command = load_command_class('django_env_server', 'envserver')

    def test_env_server_command_exists(self):
        self.assertIsInstance(self.command, BaseCommand)

    def test_env_server_loads_environment_variables(self):
        self.command.load_dotenv()
        self.assertEqual(os.environ['KEY1'], 'value_of_key_1')
        self.assertEqual(os.environ['KEY2'], 'value_of_key_2')
        self.assertEqual(os.environ['KEY3'], 'value_of_key_3')


if __name__ == '__main__':
    unittest.main()
