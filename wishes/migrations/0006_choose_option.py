# Generated by Django 4.2.1 on 2023-05-25 10:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wishes', '0005_voteoption_description_vote_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Choose_option',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_text', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chosen_by', to='wishes.voteoption')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chosen_options', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]