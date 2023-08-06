# encoding: utf-8

from django.core.management.base import BaseCommand
from optparse import make_option
from okscraper_django.models import ScraperRun, ScraperRunLog
from datetime import datetime
import logging

from okscraper.cli.runner import DbLogRunner, LogRunner

class DjangoDbLogRunner(DbLogRunner):

    def post_init(self):
        scraper_label = self._module_name
        if self._scraper_class_name != 'MainScraper':
            scraper_label = '%s %s' % (scraper_label, self._scraper_class_name)
        self._scraperrun = ScraperRun(scraper_label=scraper_label)
        self._scraperrun.save()

    def on_dblog_emit(self, record):
        """@type record: logging.Record"""
        runlog = ScraperRunLog(text=record.getMessage(), status=record.levelname)
        runlog.save()
        self._scraperrun.logs.add(runlog)
        self._scraperrun.save()

    def post_run(self):
        self._scraperrun.end_time = datetime.now()
        self._scraperrun.save()

class Command(BaseCommand):

    args = 'module [class] [arg]..'

    option_list = BaseCommand.option_list + (
        make_option(
            '--dblog', action='store_true', dest="dblog", default=False,
            help='log run details to db for monitoring of scraper jobs'
        ),
    )

    def handle(self, *args, **options):
        runnerArgs = [args[0], args[1] if len(args)>1 else None]
        runnerKwargs = {
            'log_verbosity': options.get('verbosity', '1'),
            'log_handler': logging.StreamHandler()
        }
        if options.get('dblog', False):
            runner = DjangoDbLogRunner(*runnerArgs, **runnerKwargs)
        else:
            runner = LogRunner(*runnerArgs, **runnerKwargs)
        runner.run()
