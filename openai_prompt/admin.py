from django.contrib import admin

from openai_prompt.models import OpenaiModel

# Register your models here.
admin.site.register(OpenaiModel)
