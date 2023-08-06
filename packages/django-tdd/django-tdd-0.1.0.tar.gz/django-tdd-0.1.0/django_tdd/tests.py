from django.test import TestCase
from django.core.management import call_command

class TDDTestCase(TestCase):
    """
    The most meta test case ever. Test that 'python manage.py tdd'
    runs any tests in the project then starts the development server
    """
    def setUp(self):
        pass

    def test_command_runs_tests_and_starts_server(self):
        # get the './manage.py test' output

        # get the './manage.py runserver' output

        # get the './manage.py tdd' output

        # make sure the latter contains both of former
        self.fail("FINISH THE TEST")

