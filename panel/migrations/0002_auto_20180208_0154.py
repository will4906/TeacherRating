# Generated by Django 2.0.2 on 2018-02-07 17:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='test2',
            name='test1',
        ),
        migrations.DeleteModel(
            name='Test1',
        ),
        migrations.DeleteModel(
            name='Test2',
        ),
    ]