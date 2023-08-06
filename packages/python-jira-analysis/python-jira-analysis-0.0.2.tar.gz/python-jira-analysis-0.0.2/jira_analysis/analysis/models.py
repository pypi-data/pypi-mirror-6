from django.db import models
from django.contrib.auth.models import User

from fields import SeparatedValuesField

class ProjectRecordManager(models.Manager):
    pass
    # def latest(self, project):
    #     try:
    #         return self.filter(project=project).order_by('-timestamp')[0]
    #     except:
    #         return None

class ProjectRecord(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # project and version are blank for global data
    project = models.CharField(max_length=512, blank=True) #project Key
    version = models.CharField(max_length=512, blank=True)

    data = models.TextField()

    objects = ProjectRecordManager()

    def __unicode__(self):
        return unicode(self.project) + ", " + self.version + " [" + str(self.timestamp) + "]"


class ProjectDefinition(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(User, blank=True)
    project_key = models.CharField("JIRA project key", max_length=64,
        help_text="E.g. SOA")
    project_name = models.CharField("project name", max_length=512,
        help_text="Descriptive name")
    jql = models.CharField("JQL", max_length=2048,
        help_text="Selects items to base calculations on, e.g. \
        'type NOT IN subTaskIssueTypes()'. Do not include project name and version.")
    versions = SeparatedValuesField(token=',',
        help_text="Comma separated JIRA names for project versions. Concatenated with base JQL as \
        'AND fixVersion=VERSION'. E.g. '4.5.0, 4.6.0'")
    statuses = models.CommaSeparatedIntegerField("board statuses", max_length=256,
        help_text="Comma separated JIRA ids of statuses in order of the Kanban board.")
    startStatuses = models.CommaSeparatedIntegerField("start status ids", max_length=256,
        help_text="Comma separated JIRA ids of initial statuses, used in lead time calculations.")
    endStatuses = models.CommaSeparatedIntegerField("final status ids", max_length=256,
        help_text="Comma separated JIRA ids of final statuses, used in lead time calculations.")
    devStatuses = models.CommaSeparatedIntegerField("dev status ids", max_length=256,
        help_text="Comma separated JIRA ids of development phase statuses, used in fixing time calculations.")
    qaStatuses = models.CommaSeparatedIntegerField("QA status ids", max_length=256,
        help_text="Comma separated JIRA ids of QA phase statuses, used in fixing time calculations.")
    bugTypes = SeparatedValuesField("bug issue types", token=',', default="Bug",
        help_text="Names of work item types corresponding to bugs.")
    histogramBins = models.IntegerField("histogram bins", default=360,
        help_text="Number of histogram bins.")
    minLeadTime = models.IntegerField("min lead time length", default=60,
        help_text="Min length of lead time that will get ignored in histogram calculations \
        (assuming someone dragged work item quickly through the board).")

    def __unicode__(self):
        return unicode(self.project_key) + " (" + self.project_name + "): " + ', '.join(self.versions)

