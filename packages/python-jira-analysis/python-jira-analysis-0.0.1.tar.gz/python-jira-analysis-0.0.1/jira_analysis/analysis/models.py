from django.db import models

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
    project = models.CharField(max_length=512, blank=True)
    version = models.CharField(max_length=512, blank=True)

    data = models.TextField()

    objects = ProjectRecordManager()

    def __unicode__(self):
        return unicode(self.project) + ", " + self.version + " [" + str(self.timestamp) + "]"
