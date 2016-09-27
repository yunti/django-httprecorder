from django.db import models
from django.contrib.postgres.fields import JSONField

class ApiResponse(models.Model):
    scheme = models.CharField(max_length=10)
    hostname = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    request_headers = models.TextField()
    query = models.TextField(null=True)
    payload = models.TextField(null=True)
    status_code = models.IntegerField()
    response_headers = models.TextField()
    response_json = JSONField(null=True)
    response_text = models.TextField(null=True)
    time_stamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-time_stamp']

    def __str__(self):
        return self.path
