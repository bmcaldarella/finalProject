# Generated by Django 4.2.1 on 2023-08-05 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wishes', '0020_alter_create_vote_namevote'),
    ]

    operations = [
        migrations.AddField(
            model_name='choose_option',
            name='has_voted',
            field=models.BooleanField(default=False),
        ),
    ]