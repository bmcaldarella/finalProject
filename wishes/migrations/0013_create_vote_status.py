# Generated by Django 4.2.1 on 2023-05-30 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wishes', '0012_remove_choose_option_vote'),
    ]

    operations = [
        migrations.AddField(
            model_name='create_vote',
            name='status',
            field=models.CharField(choices=[('abierto', 'Abierto'), ('cerrado', 'Cerrado')], default='abierto', max_length=20),
        ),
    ]
