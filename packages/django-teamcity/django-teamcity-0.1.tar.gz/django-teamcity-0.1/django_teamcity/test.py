from discover_runner import DiscoverRunner
import unittest
from teamcity import is_running_under_teamcity
from teamcity.unittestpy import TeamcityTestRunner
import settings


class DiscoverTeamcityRunner(DiscoverRunner):
    def __init__(self, *args, **kwargs):

        if kwargs['with_selenium']:
            settings.WITH_SELENIUM = True
        super(DiscoverTeamcityRunner, self).__init__(*args, **kwargs)

    def run_suite(self, suite, **kwargs):
        if is_running_under_teamcity():
            runner = TeamcityTestRunner
        else:
            runner = unittest.TextTestRunner
            return runner(verbosity=self.verbosity,
                          failfast=self.failfast,
                          ).run(suite)
    

