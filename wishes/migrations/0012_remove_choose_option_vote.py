# Generated by Django 4.2.1 on 2023-05-30 09:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wishes', '0011_choose_option_vote'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='choose_option',
            name='vote',
        ),
    ]