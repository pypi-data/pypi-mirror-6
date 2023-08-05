from django.core.management.commands.test import Command as TestCommand
import os
from optparse import make_option
import sys

class Command(TestCommand):
    option_list = TestCommand.option_list + (
        make_option('--with-selenium',
                    action='store_true', dest='with_selenium', default=None,
                    help='Set this option to enable test only for SeleniumTestCase subclass'
                    ),)

    def handle(self, *test_labels, **options):
        from django.conf import settings
        from django.test.utils import get_runner

        TestRunner = get_runner(settings, options.get('testrunner'))
 
        options['verbosity'] = int(options.get('verbosity'))

        if options.get('liveserver') is not None:
            os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = options['liveserver']
            del options['liveserver']

        test_runner = TestRunner(**options)
        failures = test_runner.run_tests(test_labels)

        if failures:
            sys.exit(bool(failures))
