# Generated by Django 4.2.1 on 2023-05-24 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wishes', '0004_voteoption'),
    ]

    operations = [
        migrations.AddField(
            model_name='voteoption',
            name='description_vote',
            field=models.CharField(default='Default Description', max_length=700),
        ),
        migrations.AddField(
            model_name='voteoption',
            name='image_description',
            field=models.ImageField(default='voteDefault.jpeg', upload_to=''),
        ),
    ]
