# encoding: utf-8

from django.db import models

class ScraperRun(models.Model):
    scraper_label = models.CharField(blank=False, null=False, max_length=20)
    start_time = models.DateTimeField(blank=False, null=False, auto_now=True)
    end_time = models.DateTimeField(blank=True, null=True)
    logs = models.ManyToManyField('okscraper_django.ScraperRunLog')

    def __str__(self):
        start_time = self.start_time.strftime('%d/%m/%y %H:%M')
        status = 'SUCCESS'
        failedLogs = self.logs.exclude(status='INFO')
        if failedLogs.count() > 0:
            status = failedLogs.order_by('-id')[0].status
        return '%s | %s | %s'%(self.scraper_label, start_time, status)

class ScraperRunLog(models.Model):
    time = models.DateTimeField(blank=False, null=False, auto_now=True)
    text = models.TextField(blank=False, null=False)
    status = models.CharField(blank=False, null=False, max_length=10)

    def __str__(self):
        return '%s: %s \n'%(self.status, self.text)