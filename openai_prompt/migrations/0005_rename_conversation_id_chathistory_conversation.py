# Generated by Django 4.2.1 on 2023-06-01 16:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openai_prompt', '0004_alter_chathistory_content'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chathistory',
            old_name='conversation_id',
            new_name='conversation',
        ),
    ]