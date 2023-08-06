from django.contrib import admin
from analysis.models import ProjectRecord


class ProjectRecordAdmin(admin.ModelAdmin):
    pass

admin.site.register(ProjectRecord, ProjectRecordAdmin)
