# encoding: utf-8

from django.contrib import admin
from models import ScraperRun

class ScraperRunAdmin(admin.ModelAdmin):

    readonly_fields = ScraperRun._meta.get_all_field_names()

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(ScraperRun, ScraperRunAdmin)
