# Generated by Django 4.2.1 on 2023-06-01 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openai_prompt', '0003_chathistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chathistory',
            name='content',
            field=models.CharField(blank=True, max_length=999, null=True),
        ),
    ]
