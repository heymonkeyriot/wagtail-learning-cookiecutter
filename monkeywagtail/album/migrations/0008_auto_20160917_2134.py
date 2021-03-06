# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-17 20:34
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('album', '0007_auto_20160917_1831'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genreclassalbumrelationship',
            name='page',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='album_genre_relationship', to='album.Album'),
        ),
        migrations.AlterField(
            model_name='subgenreclassalbumrelationship',
            name='page',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='album_subgenre_relationship', to='album.Album'),
        ),
    ]
