from .settings import WITH_SELENIUM
import unittest
from django.test import LiveServerTestCase


@unittest.skipUnless(WITH_SELENIUM, "no --with-selenium flag")
class SeleniumTestCase(LiveServerTestCase):
    pass
