from django.db import models

# Create your models here.
#


class OpenaiModel(models.Model):
    waid = models.CharField(max_length=64, blank=True, null=True)
    conversation_id = models.CharField(max_length=15, blank=True, null=True)


class ChatHistory(models.Model):
    conversation = models.ForeignKey(OpenaiModel,
                                     on_delete=models.CASCADE, blank=True, null=True)
    role = models.CharField(max_length=15, blank=True, null=True)
    content = models.CharField(max_length=999, blank=True, null=True)
