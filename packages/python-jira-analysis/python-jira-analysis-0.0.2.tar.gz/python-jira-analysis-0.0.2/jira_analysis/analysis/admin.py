from django.contrib import admin
from analysis.models import ProjectRecord, ProjectDefinition


class ProjectRecordAdmin(admin.ModelAdmin):
    pass

class ProjectDefinitionAdmin(admin.ModelAdmin):
    pass

admin.site.register(ProjectRecord, ProjectRecordAdmin)
admin.site.register(ProjectDefinition, ProjectDefinitionAdmin)
