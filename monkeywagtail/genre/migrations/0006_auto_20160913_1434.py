# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-13 13:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genre', '0005_auto_20160911_1623'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subgenreclass',
            old_name='subgenre',
            new_name='title',
        ),
        migrations.AddField(
            model_name='subgenreclass',
            name='slug',
            field=models.SlugField(allow_unicode=True, default='', help_text='The name of the page as it will appear in URLs e.g http://domain.com/blog/[my-slug]/', max_length=255),
            preserve_default=False,
        ),
    ]
