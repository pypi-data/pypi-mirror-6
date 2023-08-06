# encoding: utf-8

from django.utils import unittest
from okscraper_django.management.commands.okscrape import Command
from okscraper_django.models import ScraperRun

class ManagementTestCase(unittest.TestCase):

    def test(self):
        command = Command()
        command.handle('okscraper_django.tests', dblog=True)
        self.assertRegexpMatches(r'^okscraper_django.tests | [0-9][0-9]/[0-9][0-9]/[0-9][0-9] [0-9][0-9]:[0-9][0-9] | ERROR$', str(ScraperRun.objects.all()[0]))
