# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-15 23:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('album', '0004_genreclassalbumrelationship_subgenreclassalbumrelationship'),
        ('review', '0012_auto_20160915_1122'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewExperiment',
            fields=[
                ('album_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='album.Album')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('AlbumRelationship', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_album_experiment', to='review.ReviewPage')),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
            bases=('album.album', models.Model),
        ),
        migrations.RenameField(
            model_name='reviewauthorrelationship',
            old_name='authorRelationship',
            new_name='page',
        ),
        migrations.AlterField(
            model_name='reviewauthorrelationship',
            name='author',
            field=models.ForeignKey(help_text='The author who wrote this', on_delete=django.db.models.deletion.CASCADE, related_name='author_review_relationship', to='author.Author'),
        ),
    ]
